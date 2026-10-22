# Series INDEC Argentina en CSV: IPC, salarios, canastas y EMAE listos para planilla

Datos oficiales del **INDEC** (vía Datos Argentina, datos.gob.ar) en CSV que abren bien en Excel, Google Sheets, LibreOffice, Python o R. Sirven, por ejemplo, para **actualizar un alquiler, un sueldo o una deuda por inflación (IPC)**, comparar tu sueldo con la inflación o seguir las canastas básicas. Gratis, sin registro, licencia **CC BY 4.0**.

## Últimos valores de este repositorio

| Serie | Archivo | Último período | Valor | Var. mensual | Var. interanual |
|---|---|---|---|---|---|
| IPC nivel general nacional (dic-2016 = 100) | `ipc_nivel` | 2026-08 | 12.276,766 | +1,7 % | +33,5 % |
| IPC regulados nacional (dic-2016 = 100) | `ipc_regulados` | 2026-08 | 12.935,9719 | +2,2 % | +43,7 % |
| Índice de salarios (oct-2016 = 100) | `salarios` | 2026-07 | 9.708,64 | +2,8 % | +36,2 % |
| Canasta básica alimentaria, adulto equivalente ($) | `cba` | 2026-08 | 235.103,36 | +2,6 % | +39,6 % |
| Canasta básica total, adulto equivalente ($) | `cbt` | 2026-08 | 519.578,43 | +2,6 % | +38,3 % |
| EMAE desestacionalizado (2004 = 100) | `emae_desest` | 2026-07 | 149,648 (redondeado) | −2,9 % | −1,2 % |

Los valores son los de `data/` tal como los publica la fuente (el EMAE, redondeado a tres decimales). Las variaciones están calculadas con esos mismos valores (redondeadas a un decimal) y no son cifras oficiales del INDEC. Si INDEC ya publicó un mes más nuevo, la fuente manda.

## Cómo actualizar un monto por IPC

La cuenta es siempre la misma:

```
monto actualizado = monto original × IPC (mes final) ÷ IPC (mes inicial)
```

El índice está en `data/ipc_nivel.csv` (o `ipc_nivel_es-AR.csv` si tu planilla usa coma decimal). Qué meses usar (por ejemplo, el último índice publicado antes de la fecha de ajuste) lo define tu contrato o acuerdo, no este repositorio.

### Alquiler

Un alquiler de **$500.000** pactado en febrero de 2026 que se ajusta por IPC hasta agosto de 2026:

```
500.000 × 12.276,766 ÷ 10.714,6255 = 572.897,58   (+14,6 %)
```

### Sueldo

¿Cuánto tendría que cobrar hoy alguien que en agosto de 2025 cobraba **$1.000.000** para mantener el poder de compra?

```
1.000.000 × 12.276,766 ÷ 9.193,2441 = 1.335.411,73   (+33,5 %)
```

Y para ver si los salarios le ganaron a la inflación, se comparan los dos índices en el mismo período. De julio de 2025 a julio de 2026 el índice de salarios subió 36,2 % (9.708,64 ÷ 7.129,22) y el IPC 33,8 % (12.076,3937 ÷ 9.023,973): en promedio, el salario real subió alrededor de 1,8 % (1,3618 ÷ 1,3383).

### Deuda

Una deuda de **$200.000** de diciembre de 2025 actualizada por IPC a agosto de 2026:

```
200.000 × 12.276,766 ÷ 10.121,3715 = 242.590,96   (+21,3 %)
```

### En la planilla

En Google Sheets podés traer la serie directo desde este repositorio:

```
=IMPORTDATA("https://raw.githubusercontent.com/ventolabs-hq/series-indec-argentina/main/data/ipc_nivel.csv")
```

Eso deja `periodo` en la columna A, `fecha` en B y `valor` en C. Después, con el monto en `E1`, el mes inicial en `E2` y el mes final en `E3` (escritos como `202602` y `202608`):

```
=E1 * BUSCARV(E3; A:C; 3; FALSO) / BUSCARV(E2; A:C; 3; FALSO)
```

(En Excel en inglés o con configuración regional de EE. UU.: `VLOOKUP` y `,` como separador. Si `IMPORTDATA` lee mal los decimales, cambiá la configuración regional de la hoja o descargá `ipc_nivel_es-AR.csv`.)

En Python:

```python
import pandas as pd
url = "https://raw.githubusercontent.com/ventolabs-hq/series-indec-argentina/main/data/ipc_nivel.csv"
ipc = pd.read_csv(url, dtype={"periodo": str}).set_index("periodo")["valor"]
print(500_000 * ipc["202608"] / ipc["202602"])  # 572897.58...
```

Estos ejemplos son solo cuentas con datos públicos. No son asesoramiento legal, contable ni financiero.

## Las 7 series

| Archivo | Serie | Id en Datos Argentina | Frecuencia | Unidad | Desde | Hasta* |
|---|---|---|---|---|---|---|
| `ipc_nivel` | IPC nivel general nacional | `148.3_INIVELNAL_DICI_M_26` | mensual | índice dic-2016 = 100 | 2016-12 | 2026-08 |
| `ipc_regulados` | IPC regulados nacional | `148.3_IREGULANAL_DICI_M_22` | mensual | índice dic-2016 = 100 | 2016-12 | 2026-08 |
| `emae_desest` | EMAE desestacionalizado | `143.3_NO_PR_2004_A_31` | mensual | índice 2004 = 100 | 2016-12 | 2026-07 |
| `salarios` | Índice de salarios | `149.1_TL_INDIIOS_OCTU_0_21` | mensual | índice oct-2016 = 100 | 2016-12 | 2026-07 |
| `cba` | Canasta básica alimentaria (adulto equivalente) | `150.1_CSTA_BARIA_0_D_26` | mensual | pesos corrientes | 2016-12 | 2026-08 |
| `cbt` | Canasta básica total (adulto equivalente) | `150.1_CSTA_BATAL_0_D_20` | mensual | pesos corrientes | 2016-12 | 2026-08 |
| `expo_total` | Exportaciones totales | `350.1_TOTAL_EXPO_PP__22` | anual | millones de USD | 2017 | 2024 |

\* Último período en la versión actual de este repositorio. La fuente de verdad siempre es la publicación del INDEC.

## Formato de los archivos (`data/`)

Para cada serie hay dos archivos con las mismas filas:

| Archivo | Separador | Decimal | Columna `fecha` | Codificación |
|---|---|---|---|---|
| `<serie>.csv` | `,` | `.` | `AAAA-MM-DD` (ISO) | UTF-8, fin de línea LF |
| `<serie>_es-AR.csv` | `;` | `,` | `DD/MM/AAAA` | UTF-8 con BOM, fin de línea CRLF |

Columnas:

- `periodo`: año y mes como `AAAAMM` (por ejemplo `202608`). En la serie anual el mes es `01`.
- `fecha`: primer día del período.
- `valor`: el valor publicado, sin redondear ni modificar.

Usá `_es-AR.csv` si tu planilla está en configuración regional Argentina (si no, `12276.766` se puede leer como 12.276.766). Los períodos que la API devuelve sin dato no aparecen como fila.

`data/FUENTES.json` guarda, para cada serie, la licencia, la fuente y el dataset tal como los informa la metadata de la API.

## Actualización

INDEC publica la mayoría de estas series una vez por mes (calendario en indec.gob.ar). Después de cada publicación se corre:

```bash
python3 scripts/actualizar_series.py
```

El script usa solo la biblioteca estándar de Python 3.9+, respeta `robots.txt`, hace un pedido por serie a `https://apis.datos.gob.ar/series/api/series/` y:

- verifica que cada serie siga con licencia CC BY 4.0 y fuente INDEC (si no, no escribe nada);
- reintenta cuando la API devuelve valores nulos sueltos y nunca borra períodos que ya estaban en `data/`;
- reescribe solo los archivos que cambiaron.

Opciones: `--salida CARPETA` para escribir en otro lado y `--desde-cache CARPETA` para reconstruir sin red a partir de respuestas JSON guardadas.

## Fuente y atribución

**Fuente primaria: Instituto Nacional de Estadística y Censos (INDEC)**, vía la API de Series de Tiempo de Datos Argentina (datos.gob.ar), Subsecretaría de Programación Macroeconómica. Licencia de los datos: [Creative Commons Atribución 4.0 Internacional](https://creativecommons.org/licenses/by/4.0/deed.es).

Cambios respecto de la fuente: selección de series, recorte desde diciembre de 2016, omisión de períodos sin dato y conversión a dos formatos CSV. Los valores no se modifican. Este repositorio no es un producto del INDEC ni de Datos Argentina, y no tiene relación oficial con ellos.

Si reutilizás estos datos, citá al INDEC como fuente primaria, por ejemplo: «Fuente: INDEC, vía Datos Argentina (datos.gob.ar), CC BY 4.0».

Detalle en [`LICENSE-DATA.md`](LICENSE-DATA.md). El código (`scripts/`) tiene licencia [MIT](LICENSE).

Los datos se publican tal cual, sin garantía. No constituyen asesoramiento de ningún tipo.

---

## English

Official Argentine economic series from **INDEC** (CPI, regulated-prices CPI, EMAE activity index, wages index, basic food and total baskets, annual exports), pulled from the Datos Argentina time-series API and stored as CSV in two flavours: `<series>.csv` (comma, dot decimal, ISO dates) and `<series>_es-AR.csv` (semicolon, comma decimal, DD/MM/YYYY, UTF-8 BOM). Columns: `periodo` (YYYYMM), `fecha`, `valor` (unmodified published value). Refresh monthly with `python3 scripts/actualizar_series.py` (stdlib only, robots-aware, licence-checked, never drops existing periods). Data: CC BY 4.0, primary source INDEC via Datos Argentina; code: MIT. Not an official INDEC product.
