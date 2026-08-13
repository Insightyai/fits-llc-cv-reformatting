# CVs de Prueba

CVs originales (sin convertir) usados para probar el agente de transformación. No tienen branding ni formato de FITS — son el input que el agente debe procesar.

| Archivo | Notas |
|---|---|
| `Resume- Shirley Mercado.pdf` | CV real de prueba — en inglés, primera persona, sin formato FITS |
| `Resume- Ruth Sotomayor Clavell.pdf` | CV real, candidata en etapa real "8. CONVERT RESUME-BD FORMAT" (job "Buyer", `jobId 10956256`) — usado para la calibración fina de BD Format (12 ago 2026), encontró el bug de `town` ausente (ver `templates/TAG-CONTRACT.md`) |
| `Ruth Sotomayor Clavell - BD Format (render de prueba).docx` | Salida real del pipeline (`extract.py` → `agent.py` → `blocks.py` → render) para el CV de arriba, con el fix de `town` ya aplicado — para revisión visual, no es canon |
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
