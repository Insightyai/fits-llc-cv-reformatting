# CVs de Prueba

CVs originales (sin convertir) usados para probar el agente de transformación. No tienen branding ni formato de FITS — son el input que el agente debe procesar.

| Archivo | Notas |
|---|---|
| `Resume- Shirley Mercado.pdf` | CV real de prueba — en inglés, primera persona, sin formato FITS |
| `Resume- Ruth Sotomayor Clavell.pdf` | CV real, candidata en etapa real "8. CONVERT RESUME-BD FORMAT" (job "Buyer", `jobId 10956256`) — usado para la calibración fina de BD Format (12 ago 2026), encontró el bug de `town` ausente (ver `templates/TAG-CONTRACT.md`) |
| `Ruth Sotomayor Clavell - BD Format (render de prueba).docx` | Salida real del pipeline (`extract.py` → `agent.py` → `blocks.py` → render) para el CV de arriba, con el fix de `town` ya aplicado — para revisión visual, no es canon |
| `Resume- Yajaira Ortiz Ruiz.pdf` | CV real, candidata en etapa real "8. CONVERT RESUME-NON TEMPLATE" (job "Process Development Scientist -04", `jobId 10957423`, `candidateId 422900145`) — usado para verificar la calibración fina de Non Template (14 ago 2026) contra un caso real con 20 años de experiencia y 5 empresas distintas |
| `Yajaira Ortiz Ruiz - Non Template (render de prueba).docx` | Salida real del pipeline (`extract.py` → `agent.py` → `blocks.py` → render) para el CV de arriba, con el template ya calibrado — para revisión visual, no es canon. `state=review` (warnings `TOWN_NOT_DECLARED` y `SUMMARY_CLAIM_NOT_VERIFIED`, ninguno bloqueante); `certifications: []` en este candidato, buen caso real para el loop vacío |
| `Resume- Luis Antonio Garcia Sanchez.pdf` | CV real, candidato en etapa real "9. CONVERT RESUME-NEW FORMAT" (job "Project Engineer - Automation", `jobId 10938145`, `candidateId 431914011`) — usado para re-verificar New Format en local (14 ago 2026). Primer intento bloqueado por `GROUNDING_FAILED` (falso positivo real, ver `agente/CONTRATO-AGENTE.md` y `grounding.py`); corregido y re-verificado |
| `Luis Antonio Garcia Sanchez - New Format (render de prueba).docx` | Salida real del pipeline para el CV de arriba, tras el fix de grounding — para revisión visual, no es canon. `state=review` (warnings no bloqueantes: `TOWN_NOT_DECLARED`, `SUMMARY_REWRITTEN`, `YEARS_EXPERIENCE_UNKNOWN` por "Summer 2015", `COMPANY_NOT_VERIFIABLE` para skills de 2 letras `NX`/`C++`, `SECTION_COVERAGE_LOW`, `SUMMARY_CLAIM_NOT_VERIFIED`) |
| `sinteticos/` | 4 CVs sintéticos (Fase 5), uno por cada regla de contenido del PRD — ver tabla abajo |

El PRD (`../../PRD.md`) pide un set de 15–20 CVs reales para las pruebas de aceptación del Módulo 2 (Fase 7). Agregar aquí cada uno a medida que FITS los envíe.

## `sinteticos/` — harness de la Fase 5

CVs inventados a mano (sin datos reales de candidatos) para poder medir el cumplimiento de las 4 reglas de contenido del agente sin depender del set real de FITS, que todavía no llegó. Cada uno ejercita una regla distinta o una combinación, y ninguno inventa información inexistente (nombres, empresas y fechas son ficticios pero coherentes — el grounding check se corre igual contra el texto de cada archivo). Ver `tests/test_synthetic_harness.py` (marcado `llm`, opt-in).

| Archivo | Regla(s) que ejercita |
|---|---|
| `01-espanol-objetivo-primera-persona.txt` | Regla 1 (traducción) + Regla 2 (tercera persona) + Regla 3 (Objective → Summary) combinadas |
| `02-ingles-i-statements-summary-bueno.txt` | Regla 2 sola — ya en inglés, ya trae un Summary profesional (no debería reescribirse) |
| `03-ingles-objective-sin-i-statements.txt` | Regla 3 sola — ya en inglés, bullets ya impersonales |
| `04-ingles-summary-pobre.txt` | Regla 4 sola — Summary existente pero pobre/genérico |
