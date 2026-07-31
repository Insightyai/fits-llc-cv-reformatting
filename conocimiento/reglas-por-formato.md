# Reglas de Contenido por Formato

> Consolida las 4 reglas universales del PRD con las particularidades encontradas al inspeccionar los templates (`anatomia-templates.md`) y el mapeo de placeholders (`../02-modulo2-agente-transformacion/templates/MAPEO-PLACEHOLDERS.md`). Referencia para el prompt de transformación (`../02-modulo2-agente-transformacion/prompt/transform-v1.md`, ver contrato en `../02-modulo2-agente-transformacion/agente/CONTRATO-AGENTE.md`).

## Reglas universales (aplican a los 3 formatos activos: New Format, Non Template, BD Format)

Del PRD (`Módulo 2`), en orden de aplicación:

1. **Traducción al inglés** si el CV original está en otro idioma. El resultado final siempre está en inglés, sin importar el idioma de origen.
2. **Conversión a tercera persona** — eliminar I-statements ("I managed a team of 5" → "Managed a team of 5" / "He/She managed a team of 5", a definir estilo exacto con FITS vía los CVs de ejemplo pendientes).
3. **Objectives → Summary profesional** — si el CV trae una sección "Objective" (típico de CVs en primera persona, poco profesionales), se reemplaza por un "Summary" redactado en tono profesional de reclutamiento, no se traduce literalmente.
4. **Reescritura de summaries pobres o incompletos** — si ya existe un Summary pero es débil (muy corto, genérico, mal redactado), se reescribe. Este es el único campo evaluado por aprobación humana (≥90%, no automática) — ver `PRD.md` §Módulo 2, "Por qué el criterio no es simplemente 95% de precisión".

**No inventar información.** Ninguna de las 4 reglas autoriza agregar experiencia, empresas, fechas o títulos que no estén en el CV original — son reglas de forma (idioma, persona gramatical, tono), no de contenido. Ver `../02-modulo2-agente-transformacion/microservicio/grounding.py` (Fase 3 del plan de implementación del agente, `agente/CONTRATO-AGENTE.md`) para la validación determinística de esto.

## Regla especial — BD Format (Becton Dickinson)

El template `BD - Resume Template.docx` no tiene sección "Skills" separada — está fusionada con el Summary en una sola sección "Summary of Skills" (ver anatomía). La regla de negocio (ya documentada en el README de Módulo 2 y en el mapeo de placeholders) es:

> El pueblo de residencia del candidato se incluye dentro de "Summary of Skills", no en una sección propia.

Esto significa que `town` se extrae **siempre** (los 3 formatos activos podrían tenerlo disponible en el JSON canónico), pero **solo el template BD lo renderiza**. La regla vive en el mapeo de placeholders del template (`{% if town %} Resides in {{ town }}.{% endif %}`), no en el prompt — el LLM no necesita saber qué formato se está generando.

## Diferencia estructural — New Format / Non Template vs. BD Format

- **New Format y Non Template** separan Education y Licenses/Certifications en dos secciones distintas.
- **BD Format** las fusiona en una sola sección "Education/Certifications/Licenses".

Esto es puramente de presentación (resuelto en el template al renderizar `education[]` + `certifications[]` juntos o separados) — no cambia lo que el LLM extrae.

## Campo no cubierto por las 4 reglas del PRD: `years_experience`

New Format y Non Template requieren un valor tipo "8+ YRS. OF EXP." en el header. Ninguna de las 4 reglas de contenido del PRD lo menciona — es una exigencia del layout del template, no una regla de transformación de contenido.

**Pendiente de definir con FITS:** cómo se calcula (suma de todos los períodos de `experience[]`, sin solapamientos, redondeado hacia abajo; o el candidato lo declara en su CV original y se copia tal cual si está presente). Hasta confirmar, el criterio v1 (ver `agente/CONTRATO-AGENTE.md`) lo calcula de la forma más conservadora (a partir de fechas explícitas en el CV, solo el número sin el sufijo `+` que ya agrega el template) y deja constancia en `_meta.warnings` (`YEARS_EXPERIENCE_UNKNOWN`) si no puede determinarse con confianza, en vez de inventar un número.

## Formato sin reglas propias: Worksense

No integrado en JazzHR (ver `Decisiones.md`) — no tiene candidatos que lleguen a esa etapa, por lo tanto no hay reglas de contenido específicas que documentar más allá del layout (`anatomia-templates.md`). Si se reactiva, revisar esta sección.

## Validación de calidad (para la aprobación ≥90% de FITS)

No hay todavía una guía de estilo objetiva más allá de las 4 reglas — depende de los CVs de ejemplo ya convertidos que Paola se comprometió a enviar (pendiente, ver `PRD.md` §5). Hasta que lleguen, el prompt v1 (Fase 3.1 del plan) se basa únicamente en las 4 reglas del PRD; se ajusta cuando lleguen los ejemplos, como iteración normal de prompt (no como bug).
