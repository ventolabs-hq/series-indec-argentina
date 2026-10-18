# Series INDEC Argentina (CSV abiertos)

Series económicas oficiales de Argentina publicadas por el **INDEC**, descargadas de la API de Series de Tiempo de **Datos Argentina** (datos.gob.ar) y ordenadas en CSV listos para Excel, Google Sheets, LibreOffice, Python o R. Gratis, con licencia **CC BY 4.0**.

- 7 series mensuales/anuales desde diciembre de 2016: IPC, IPC regulados, EMAE, salarios, canastas y exportaciones.
- Cada serie en **dos formatos**: internacional (`,` y punto decimal) y Argentina (`;` y coma decimal).
- Un script sin dependencias para volver a descargarlas cuando INDEC publica datos nuevos.

## Series

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
