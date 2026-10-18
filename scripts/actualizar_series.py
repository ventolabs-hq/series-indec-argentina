#!/usr/bin/env python3
"""Actualiza las series INDEC de data/ desde la API de Series de Tiempo de Datos Argentina.

Uso:
  python3 scripts/actualizar_series.py                    # descarga en vivo y reescribe data/ solo si cambió algo
  python3 scripts/actualizar_series.py --desde-cache DIR  # sin red: usa DIR/<clave>.json (respuestas guardadas de la API)
  python3 scripts/actualizar_series.py --salida OTRA_DIR  # escribe en otra carpeta (por defecto: data/)
  python3 scripts/actualizar_series.py --guardar-json DIR # además guarda las respuestas crudas de la API en DIR

Solo biblioteca estándar de Python 3.9+. Respeta robots.txt y Crawl-delay (mínimo 1 s entre pedidos).
Antes de escribir verifica, para cada serie, que la licencia sea CC BY 4.0 y que la fuente sea INDEC.

Códigos de salida: 0 ok · 2 fuente inaccesible · 3 licencia/fuente no válida o robots.txt no permite ·
                   4 datos vacíos o con huecos (la API a veces devuelve nulos sueltos o la serie en blanco; se reintenta
                     hasta 6 veces con espera creciente y nunca se toma un valor en blanco como dato).
Si falla cualquier serie no se escribe ningún archivo. Una actualización nunca borra períodos que ya estaban en data/.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser
from datetime import datetime, timezone
from pathlib import Path

API = "https://apis.datos.gob.ar/series/api/series/"
UA = "series-indec-argentina/1.0 (actualizacion mensual de datos abiertos)"
START = "2016-12-01"
SERIES = [
    # clave, id de serie en Datos Argentina, descripción
    ("ipc_nivel", "148.3_INIVELNAL_DICI_M_26", "IPC nivel general nacional (dic-2016=100)"),
    ("ipc_regulados", "148.3_IREGULANAL_DICI_M_22", "IPC regulados nacional (dic-2016=100)"),
    ("emae_desest", "143.3_NO_PR_2004_A_31", "EMAE desestacionalizado (2004=100)"),
    ("salarios", "149.1_TL_INDIIOS_OCTU_0_21", "Índice de salarios (oct-2016=100)"),
    ("cba", "150.1_CSTA_BARIA_0_D_26", "Canasta básica alimentaria, adulto equivalente ($)"),
    ("cbt", "150.1_CSTA_BATAL_0_D_20", "Canasta básica total, adulto equivalente ($)"),
    ("expo_total", "350.1_TOTAL_EXPO_PP__22", "Exportaciones totales (millones de USD, anual)"),
]
LICENCIAS_OK = {"creative commons attribution 4.0", "cc-by-4.0", "cc by 4.0"}
FUENTE_OK = re.compile(r"Instituto Nacional de Estad[ií]stica y Censos|\bINDEC\b", re.I)
FUENTE_NO = re.compile(r"Banco Central|\bBCRA\b", re.I)
ROOT = Path(__file__).resolve().parent.parent
INTENTOS = 6  # la API a veces devuelve nulos sueltos o una serie entera en blanco (EMAE, 2026-10-18): se reintenta
ESPERA_BASE = 2.0  # backoff exponencial entre reintentos de una misma serie: 2, 4, 8, 16, 32 s (más el Crawl-delay)


class Falla(Exception):
    def __init__(self, code: int, msg: str):
        super().__init__(msg)
        self.code = code


def _get(url: str, timeout: int = 60) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def robots_ok(url: str) -> float:
    """Devuelve el Crawl-delay; lanza Falla si robots.txt no permite o no se puede leer (5xx/red)."""
    host = urllib.parse.urlsplit(url).netloc
    rp = urllib.robotparser.RobotFileParser()
    try:
        rp.parse(_get(f"https://{host}/robots.txt", 30).decode("utf-8", "replace").splitlines())
    except urllib.error.HTTPError as e:
        if e.code >= 500:
            raise Falla(2, f"robots.txt de {host}: HTTP {e.code}") from e
        rp.parse([])  # 4xx: sin restricciones (RFC 9309)
    except Exception as e:  # noqa: BLE001
        raise Falla(2, f"robots.txt de {host}: {e!r}") from e
    if not rp.can_fetch(UA, url):
        raise Falla(3, f"robots.txt no permite {url}")
    return max(float(rp.crawl_delay(UA) or 0), 1.0)


def verificar(sid: str, meta: dict) -> dict:
    ds = meta.get("dataset") or {}
    lic, src = (ds.get("license") or "").strip(), (ds.get("source") or "").strip()
    if lic.lower() not in LICENCIAS_OK:
        raise Falla(3, f"{sid}: licencia no es CC BY 4.0 ({lic!r})")
    if not FUENTE_OK.search(src) or FUENTE_NO.search(src):
        raise Falla(3, f"{sid}: la fuente no es INDEC ({src!r})")
    if (meta.get("field") or {}).get("id") not in (None, sid):
        raise Falla(3, f"{sid}: el id de la metadata no coincide")
    return {"id": sid, "license": lic, "source": src,
            "publisher": (ds.get("publisher") or {}).get("name"), "dataset": ds.get("title")}


def a_csv(puntos: list) -> dict[str, bytes]:
    a, b = io.StringIO(), io.StringIO()
    wa, wb = csv.writer(a, lineterminator="\n"), csv.writer(b, delimiter=";", lineterminator="\r\n")
    wa.writerow(["periodo", "fecha", "valor"])
    wb.writerow(["periodo", "fecha", "valor"])
    for d, v in puntos:
        periodo = d[:4] + d[5:7]
        wa.writerow([periodo, d, repr(float(v))])
        wb.writerow([periodo, f"{d[8:10]}/{d[5:7]}/{d[:4]}", repr(float(v)).replace(".", ",")])
    return {"": a.getvalue().encode(), "_es-AR": ("\ufeff" + b.getvalue()).encode()}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--desde-cache", type=Path, help="carpeta con <clave>.json (sin red)")
    ap.add_argument("--salida", type=Path, default=ROOT / "data")
    ap.add_argument("--guardar-json", type=Path, help="guarda también la respuesta cruda de la API (<clave>.json) en esta carpeta")
    args = ap.parse_args(argv)
    archivos: dict[str, bytes] = {}
    fuentes = []
    try:
        delay = None
        for clave, sid, _ in SERIES:
            if args.desde_cache:
                body = (args.desde_cache / f"{clave}.json").read_bytes()
            else:
                # 2026-10-18: la API devuelve "data": [] de forma persistente para algunas URL exactas y responde bien a la
                # misma consulta con los parámetros en otro orden (caché del servidor). Se rota entre órdenes equivalentes.
                variantes = [
                    [("ids", sid), ("format", "json"), ("limit", 1000), ("metadata", "full"), ("start_date", START)],
                    [("ids", sid), ("format", "json"), ("limit", 1000), ("start_date", START), ("metadata", "full")],
                    [("ids", sid), ("start_date", START), ("metadata", "full"), ("format", "json"), ("limit", 1000)],
                ]
                url = API + "?" + urllib.parse.urlencode(variantes[0])
                mejor = None
                for intento in range(INTENTOS):
                    url = API + "?" + urllib.parse.urlencode(variantes[intento % len(variantes)])
                    if delay is None:
                        delay = robots_ok(url)
                    else:
                        time.sleep(delay + (ESPERA_BASE * 2 ** (intento - 1) if intento else 0))
                    try:
                        cand = _get(url)
                        filas = json.loads(cand)["data"]
                    except Exception as e:  # noqa: BLE001
                        if intento == INTENTOS - 1 and mejor is None:
                            raise Falla(2, f"{sid}: {e!r}") from e
                        print(f"{clave}: intento {intento + 1} falló ({e!r}), reintentando", file=sys.stderr)
                        continue
                    nulos = sum(r[1] is None for r in filas)
                    if not filas or nulos == len(filas):
                        print(f"{clave}: intento {intento + 1} vino en blanco, reintentando", file=sys.stderr)
                        continue
                    if mejor is None or nulos < mejor[0]:
                        mejor = (nulos, cand)
                    if nulos == 0:
                        break
                    print(f"{clave}: intento {intento + 1} con {nulos} nulo(s), reintentando", file=sys.stderr)
                if mejor is None:
                    raise Falla(4, f"{sid}: la API devolvió la serie en blanco {INTENTOS} veces; reintentar más tarde")
                body = mejor[1]
                if args.guardar_json:
                    args.guardar_json.mkdir(parents=True, exist_ok=True)
                    (args.guardar_json / f"{clave}.json").write_bytes(body)
            j = json.loads(body)
            fuentes.append(verificar(sid, j["meta"][1]))
            puntos = [(r[0], r[1]) for r in j["data"] if r[1] is not None]
            if not puntos:
                raise Falla(4, f"{sid}: sin datos")
            huecos = [r[0][:7] for r in j["data"] if r[1] is None and puntos[0][0] < r[0] < puntos[-1][0]]
            if huecos:  # un valor en blanco nunca se toma como dato ni se rellena
                raise Falla(4, f"{sid}: {len(huecos)} período(s) en blanco dentro del rango (p. ej. {huecos[0]}); "
                               f"no se escribe nada, reintentar más tarde")
            previo = args.salida / f"{clave}.csv"
            if previo.exists():
                antes = {ln.split(",")[1] for ln in previo.read_text().splitlines()[1:] if ln}
                faltan = sorted(antes - {d for d, _ in puntos})
                if faltan:
                    raise Falla(4, f"{sid}: la API no devolvió {len(faltan)} período(s) que ya están en data/ "
                                   f"(p. ej. {faltan[0][:7]}); no se sobrescribe, reintentar más tarde")
            for suf, data in a_csv(puntos).items():
                archivos[f"{clave}{suf}.csv"] = data
            print(f"{clave}: {len(puntos)} períodos, {puntos[0][0][:7]} a {puntos[-1][0][:7]}")
    except Falla as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return e.code
    archivos["FUENTES.json"] = json.dumps(fuentes, ensure_ascii=False, indent=1).encode()
    args.salida.mkdir(parents=True, exist_ok=True)
    cambios = 0
    for nombre, data in archivos.items():
        p = args.salida / nombre
        if not p.exists() or p.read_bytes() != data:
            p.write_bytes(data)
            cambios += 1
    print(f"{cambios} archivo(s) actualizados en {args.salida} ({datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
