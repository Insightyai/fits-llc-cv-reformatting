# Módulo 1 — Stage "Resumes" en los Workflows de JazzHR

**Estado:** No iniciado
**Corrección de alcance (kickoff 7 jul 2026):** ver nota abajo — no es un job posting nuevo aislado.

## Alcance

- Agregar un stage **"Resumes"** dentro de cada uno de los **10–12 workflows/pipelines de JazzHR que FITS ya tiene** (los mismos usados para AI Screening en Fase 1), no crear un job posting nuevo separado.
- Dentro del stage "Resumes", el reclutador mueve manualmente el CV al sub-formato deseado según cuál de los 4 formatos necesite:
  - **New Format** — con logo FITS, para SOW requisitions
  - **Non Template** — sin logo (Medtronic, Integra FG, Haleon FG, Beeline, Amgen FG, Abbott FG)
  - **BD Format** — Becton Dickinson
  - **Worksense Format** — Johnson & Johnson
- Acceso habilitado para todos los reclutadores

## Nota sobre el cambio de alcance

La lectura inicial del contrato ("Job Posting Centralizado 'Resumes' en JazzHR") sugería un posting nuevo, aislado. En el kickoff del 7 jul 2026, Paola confirmó explícitamente que en realidad se trata de **agregar la etapa "Resumes" a los 10-12 workflows que FITS ya tiene activos** (los mismos de Fase 1). Esto implica más superficie de cambio que un posting nuevo aislado — cualquier modificación toca pipelines que ya están en producción con el agente de screening de Fase 1 corriendo. Ver `../Decisiones.md` para el detalle completo.

El workflow de N8N que procesa el "Resumes" stage es nuevo (no reutiliza el workflow de AI Screening), pero lee un stage que vive dentro de la estructura existente de JazzHR.

## Criterio de Aceptación

El stage "Resumes" está activo y correctamente configurado en los workflows de JazzHR, y todos los reclutadores tienen acceso confirmado por el representante designado de FITS.

## No incluido

Modificación de otros stages en los workflows existentes — solo se agrega el stage "Resumes", sin tocar la lógica de AI Screening ya en producción.

## Pendientes para arrancar

1. Confirmar en cuáles de los 10-12 workflows se habilita el stage (¿todos, o un subconjunto?)
2. Un CV de ejemplo ya convertido a cada uno de los 4 formatos (Paola se comprometió a enviarlos) como caso de prueba/referencia
3. Acceso a JazzHR para configurar el nuevo stage (confirmar con Jeremy)
