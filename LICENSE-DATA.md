# Licencia y atribución de los datos (`data/`)

**Licencia:** Creative Commons Atribución 4.0 Internacional (CC BY 4.0)
https://creativecommons.org/licenses/by/4.0/deed.es · texto legal: https://creativecommons.org/licenses/by/4.0/legalcode.es

**Fuente primaria:** Instituto Nacional de Estadística y Censos (INDEC), República Argentina.
**Distribución:** Datos Argentina (datos.gob.ar), API de Series de Tiempo `https://apis.datos.gob.ar/series/api/series/`, catálogo «Datos Programación Macroeconómica» (Subsecretaría de Programación Macroeconómica).

| Archivos | Serie (id) | Dataset de origen |
|---|---|---|
| `ipc_nivel*.csv` | `148.3_INIVELNAL_DICI_M_26` | Índice de Precios al Consumidor Nacional (IPC). Base diciembre 2016 |
| `ipc_regulados*.csv` | `148.3_IREGULANAL_DICI_M_22` | Índice de Precios al Consumidor Nacional (IPC). Base diciembre 2016 |
| `emae_desest*.csv` | `143.3_NO_PR_2004_A_31` | Estimador Mensual de Actividad Económica (EMAE). Base 2004 |
| `salarios*.csv` | `149.1_TL_INDIIOS_OCTU_0_21` | Índice de salarios. Base octubre 2016 |
| `cba*.csv`, `cbt*.csv` | `150.1_CSTA_BARIA_0_D_26`, `150.1_CSTA_BATAL_0_D_20` | Valores de la Canasta Básica de Alimentos y Canasta Básica Total |
| `expo_total*.csv` | `350.1_TOTAL_EXPO_PP__22` | Exportaciones por provincia y rubro |

La licencia de cada serie se verificó en la metadata de la API (`dataset.license = "Creative Commons Attribution 4.0"`) y queda registrada en `data/FUENTES.json`. El script de actualización vuelve a verificarla en cada corrida y no escribe nada si cambia.

**Cambios realizados:** selección de series; recorte desde diciembre de 2016; omisión de períodos sin dato; conversión a CSV en dos formatos (internacional y es-AR). Los valores publicados no se modifican.

**Aviso:** este repositorio no es un producto del INDEC ni de Datos Argentina, ni cuenta con su aval. Los datos se ofrecen tal cual, sin garantía.

**Cómo citar:** «Fuente: INDEC, vía Datos Argentina (datos.gob.ar). Licencia CC BY 4.0. Datos reorganizados en series-indec-argentina.»
