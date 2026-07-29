# Mapa de Etapas "Convert Resume" en JazzHR

> Obtenido vía `GET https://api.resumatorapi.com/v1/workflows?apikey=...` (`JAZZHR_API_KEY` en `.env`) el 28 jul 2026. Confirma y completa el mapeo cualitativo de `PRD.md` §3 con los `workflow_id` y `step_id` reales que necesita el Code node de selección de template (Módulo 2).

## Las 13 etapas, con IDs reales

| Workflow | workflow_id | step_id | number | Nombre exacto de la etapa (tal como está en JazzHR) | Formato |
|---|---|---|---|---|---|
| Abbott FG - Workflow 2024 | `workflow_20240528144743_ZHRXPUV7WPL3H4QF` | `10727628` | 8 | `CONVERT RESUME-NON TEMPLATE` | Non Template |
| Amgen FG - Workflow 2024 | `workflow_20240527195729_G5PIJLQ80TBWVTTF` | `10727629` | 8 | `CONVERT RESUME-NON TEMPLATE` | Non Template |
| Becton Dickinson - Workflow 2024 | `workflow_20240522132127_UTAFYZG9FRGGLUCM` | `10727630` | 8 | `CONVERT RESUME-BD FORMAT` | BD Format |
| Beeline - Workflow 2024 | `workflow_20240527195850_NH79K94T0HUCCDYN` | `10727631` | 7 | `CONVERT RESUME-NON TEMPLATE` | Non Template |
| Haleon FG - Workflow 2026 | `workflow_20260113121345_L8PDBY2NRSD8OPNW` | `10727632` | 7 | `Convert Resume - Non Template` | Non Template |
| Haleon FG - Workflow 2026 | `workflow_20260113121345_L8PDBY2NRSD8OPNW` | `10727633` | 8 | `CONVERT RESUME-NEW FORMAT` | New Format |
| Integra FG - Workflow 2024 | `workflow_20240802152448_GZRUI1QHVMAWTQC3` | `10727634` | 7 | `CONVERT RESUME-NON TEMPLATE` | Non Template |
| JazzHR Standard Workflow | `workflow_20180926200749_TDLCNSZAGDZ81EYV` | `10727648` | 10 | `CONVERT RESUME-NON TEMPLATE` | Non Template |
| JazzHR Standard Workflow | `workflow_20180926200749_TDLCNSZAGDZ81EYV` | `10727649` | 11 | `CONVERT RESUME-NEW FORMAT` | New Format |
| JNJ - Workflow 2024 | `workflow_20240524193156_FPOXYAQA1EGM1MCO` | `10727652` | 9 | `CONVERT RESUME-NON TEMPLATE` | Non Template |
| JNJ - Workflow 2024 | `workflow_20240524193156_FPOXYAQA1EGM1MCO` | `10727653` | 10 | `CONVERT RESUME-NEW FORMAT` | New Format |
| Medtronic - Workflow 2024 | `workflow_20240524195645_7XAAQ99VTWVFLBJS` | `10727654` | 10 | `CONVERT RESUME-NON TEMPLATE` | Non Template |
| SOW Workflow 2024 | `workflow_20240620184425_NDIQGY0EF7EZQMUE` | `10727655` | 9 | `CONVERT RESUME-NEW FORMAT` | New Format |

13/13 etapas confirmadas — coincide con el conteo esperado del PRD (8 Non Template + 4 New Format + 1 BD Format).

## Hallazgo importante para el Code node de selección de template

**Los nombres de etapa NO son consistentes entre workflows.** La mayoría usa mayúsculas sin espacios (`CONVERT RESUME-NON TEMPLATE`), pero **Haleon FG - Workflow 2026** usa un formato distinto para su etapa Non Template: `Convert Resume - Non Template` (mayúsculas/minúsculas mixtas, con espacios alrededor del guion).

**Implicación de diseño:** el Code node que mapea `stageName → template` (Módulo 2 README, línea 18: "solo necesita el nombre de la etapa") **no puede hacer un match exacto de string**. Tiene que:
1. Normalizar (`.toUpperCase().replace(/[\s-]+/g, ' ').trim()`) antes de comparar, o
2. Matchear por `step_id` en vez de por nombre, usando esta tabla como diccionario fijo `step_id → formato`.

**Recomendación:** usar la opción 2 (match por `step_id`), no por nombre — es inmune a que alguien renombre una etapa en JazzHR más adelante (como pasó con JNJ en Módulo 1) y evita todo el problema de normalización de texto. El Code node lee `step_id` del payload del poller y busca en esta tabla (embebida como diccionario en el nodo, o cargada desde este archivo).

## Pendiente

Confirmar si Haleon FG (`Workflow 2026`, creado en 2026) es un workflow más nuevo con convención de nombres distinta a propósito, o un error de tipeo de quien lo configuró — no bloquea la implementación (se resuelve con match por `step_id`), pero vale la pena mencionarlo si se habla con Paola/Jeremy por otro tema.
