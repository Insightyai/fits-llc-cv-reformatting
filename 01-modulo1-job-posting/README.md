# Módulo 1 — Etapas "Convert Resume" en los Workflows de JazzHR

**Estado:** No iniciado
**Corrección de alcance (kickoff 7 jul 2026):** ver nota abajo — no es un job posting nuevo aislado.
**Mapeo confirmado (correo de Paola, 7 jul 2026):** ver tabla abajo. Ver `../Decisiones.md` para el registro completo.

## Alcance

- Agregar la(s) etapa(s) **`Convert Resume - [Formato]`** dentro de cada uno de los **10 workflows/pipelines de JazzHR que FITS ya tiene** (los mismos usados para AI Screening en Fase 1), no crear un job posting nuevo separado.
- Cada workflow solo recibe las etapas de los formatos que le aplican (no los 4 en todos):

| Workflow | Etapa(s) agregada(s) |
|---|---|
| Abbott FG - Workflow 2024 | Convert Resume - Non Template |
| Amgen FG - Workflow 2024 | Convert Resume - Non Template |
| Becton Dickinson - Workflow 2024 | Convert Resume - BD Format |
| Beeline - Workflow 2024 | Convert Resume - Non Template |
| Haleon FG - Workflow 2026 | Convert Resume - Non Template · Convert Resume - New Format |
| JazzHR Standard Workflow | Convert Resume - Non Template · Convert Resume - New Format |
| JNJ - Workflow 2024 | Convert Resume - Non Template · Convert Resume - New Format |
| Integra FG - Workflow 2024 | Convert Resume - Non Template |
| Medtronic - Workflow 2024 | Convert Resume - Non Template |
| SOW Workflow 2024 | Convert Resume - New Format |

- El reclutador mueve manualmente el CV a la etapa del formato deseado — el sistema hace el resto
- Acceso habilitado para todos los reclutadores

## Nota — Worksense Format no es una etapa nueva en JazzHR

JNJ - Workflow 2024 mantiene las mismas dos etapas que Paola envió (Non Template y New Format) — no requiere cambios en JazzHR. Worksense Format se resuelve del lado del agente de transformación: para este workflow específico, la etapa "Convert Resume - New Format" debe aplicar el template Worksense en vez del template genérico de New Format. Ver `../02-modulo2-agente-transformacion/README.md` y `../Decisiones.md`. Hipótesis a confirmar con Paola.

## Nota sobre el cambio de alcance

La lectura inicial del contrato ("Job Posting Centralizado 'Resumes' en JazzHR") sugería un posting nuevo, aislado. En el kickoff del 7 jul 2026, Paola confirmó explícitamente que en realidad se trata de **agregar etapas nuevas a los workflows que FITS ya tiene activos** (los mismos de Fase 1), y el mismo día envió por correo el mapeo exacto de workflow → etapa(s). Esto implica más superficie de cambio que un posting nuevo aislado — cualquier modificación toca pipelines que ya están en producción con el agente de screening de Fase 1 corriendo. Ver `../Decisiones.md` para el detalle completo.

El workflow de N8N que procesa estas etapas es nuevo (no reutiliza el workflow de AI Screening), pero lee etapas que viven dentro de la estructura existente de JazzHR.

## Criterio de Aceptación

Las etapas `Convert Resume - [Formato]` están activas y correctamente configuradas en los 10 workflows de JazzHR, y todos los reclutadores tienen acceso confirmado por el representante designado de FITS.

## No incluido

Modificación de otras etapas en los workflows existentes — solo se agregan las etapas `Convert Resume - [Formato]`, sin tocar la lógica de AI Screening ya en producción.

## Pendientes para arrancar

1. Confirmar con Paola que para JNJ - Workflow 2024, la etapa "Convert Resume - New Format" debe generar el template Worksense (J&J) en vez del template genérico de New Format
2. Acceso a JazzHR para configurar las nuevas etapas (confirmar con Jeremy)
