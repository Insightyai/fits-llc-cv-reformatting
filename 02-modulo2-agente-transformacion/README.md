# Módulo 2 — Agente de Transformación AI

**Estado:** No iniciado — bloqueado por templates de branding y por el sitio de SharePoint

## Alcance

- Detección automática cuando un candidato llega a cualquier stage del job posting "Resumes"
- Extracción del CV (PDF o DOCX) desde JazzHR
- Transformación del contenido vía agente AI (Anthropic/Claude):
  - Traducción al inglés si el CV está en otro idioma
  - Conversión a tercera persona (eliminación de I-statements)
  - Sustitución de Objectives por Summary profesional
  - Reescritura de summaries pobres o incompletos
- Generación programática del .docx final con los 4 templates (logo, estilos de fuente, orden de secciones por formato — incluyendo pueblo de residencia en Summary of Skills para BD Format)

## Selección de template — depende solo de la etapa

Confirmado por Paola (correo del 21 jul 2026): el formato Worksense queda descartado, no se integra en JazzHR. La etapa "Convert Resume - New Format" siempre aplica el template genérico `New Format Resume Template.docx`, sin importar el workflow — el Code node de selección de template solo necesita el nombre de la etapa. El template `Worksense Template.docx` recibido junto con los otros 3 queda sin uso por ahora (ver `../Decisiones.md`).

## Criterio de Aceptación

- Procesa un CV de prueba en menos de 3 minutos desde el trigger hasta el .docx final
- Las reglas de formato se aplican en el 100% del set de prueba acordado (15–20 CVs reales)
- La calidad de reescritura del Summary es aprobada por FITS en ≥90% del set de prueba
- El template correcto se aplica para cada uno de los 4 formatos

## Por qué el criterio no es simplemente "95% de precisión"

El borrador original mezclaba reglas binarias (medibles automáticamente) con calidad editorial (que requiere aprobación humana). Se reformuló para separar ambas: reglas de formato al 100%, calidad de reescritura del Summary con aprobación humana ≥90% sobre un set acordado — evita exponer a Insighty a reclamos por gusto editorial durante la garantía de 30 días.

## No incluido

Templates adicionales a los 4 definidos · evaluación de idoneidad del candidato (la hace el agente de screening de Fase 1) · ajustes de prompt para nuevos tipos/formatos de CV fuera del set de prueba (se cotizan aparte, no son bugs).

## Pendientes para arrancar

1. Los 4 templates .docx definitivos con branding completo
2. Set de 15–20 CVs reales acordado con FITS
3. ~~Definir si se reutiliza la credencial Anthropic de Fase 1 o se provisiona una nueva~~ — resuelto: se reutiliza `P3oMjAzU63IfOAff`
