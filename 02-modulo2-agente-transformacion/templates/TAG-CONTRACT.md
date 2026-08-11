# Contrato de Tags — Microservicio de Render

> Especificación definitiva de los tags Jinja2/`docxtpl` para los 3 templates activos (New Format, Non Template, BD Format). Reemplaza los tags de `MAPEO-PLACEHOLDERS.md` y de los `.docx` en `anotados/` (anotados el 28 jul con tags simples `{{ }}`) — ambos quedan como referencia histórica, no como fuente de verdad. Los `.docx` reales se re-anotan en Fase 2 siguiendo este documento.
>
> **Motivo del reemplazo:** la auditoría de Opus (28 jul 2026, ver `Decisiones.md` y `seguimiento/bitacora.md`) encontró que los tags simples `{{ for %}{{ }}{% endfor %}` no son compatibles con la técnica de render multilínea (`RichText`) — generan un párrafo vacío sin error, o concatenan todo el contenido en una sola línea sin separación. Este documento fue validado con renders reales (`docxtpl` 0.20.2) antes de escribirse — ver evidencia al final.
>
> **Corrección (11 ago 2026):** las secciones "Regla general" y "Regla de bloques multilínea" de más abajo describen el diseño de `RichText` del spike de Fase 2, pero **no es lo que terminó implementado** — los 3 `.docx` reales en `anotados/` usan `{% for %}...{% endfor %}` escrito directamente en el `.docx`, con cada tag Jinja en su propio párrafo (loop a nivel de párrafo, no inline dentro de un mismo párrafo). Resulta que `docxtpl` sí repite el párrafo completo por cada iteración cuando el loop vive a nivel de párrafo — el problema que el spike de `RichText` evitaba era específico de loops *inline* dentro de un mismo párrafo, no de loops a nivel de párrafo. La sangría francesa y los tab stops sobreviven igual. Se deja la sección original como referencia histórica de por qué se descartó la sintaxis simple `{{ }}`, pero la arquitectura real de bullets/loops es la de "Regla de negocio (11 ago 2026)" más abajo.

## Regla general: dos tipos de tag, sin excepciones

| Tipo de campo | Sintaxis | Ejemplos |
|---|---|---|
| **Valor simple, una sola línea, no repetible** | `{{ campo }}` | `full_name`, `summary` |
| **Lista o bloque con múltiples líneas** (bullets, loops) | `{{r nombre_block }}` (un único tag `RichText`, construido en Python) | `experience_block`, `education_block`, `certifications_block`, `skills_block` |

**Prohibido a partir de ahora:** `{% for %}...{% endfor %}` escrito directamente en el `.docx`. Cualquier campo que sea una lista se resuelve como un bloque `{{r }}` armado en Python — el microservicio recibe el JSON del `cv-schema.json`, itera ahí, y arma un único objeto `RichText` por bloque. En el `.docx` solo existe el tag `{{r nombre_block }}`, nunca lógica de loop.

## Regla obligatoria: `autoescape=True`

Todo render debe llamarse `tpl.render(context, autoescape=True)`. Sin esto, `&`, `<` y `>` se pierden en silencio en los tags `{{ }}` (bug confirmado — frecuente en el dominio farmacéutico: "J&J", "R&D", "ISO 13485 & FDA 21 CFR 820"). Con `autoescape=True` confirmado que sobrevive: `&`, `<`, `>`, comillas dobles, acentos y ñ, tanto en tags simples como dentro de `RichText`.

`RichText.add()` ya escapa su contenido internamente (indistinto del `autoescape` del render) — no hay riesgo de doble-escape porque el output pasa a XML crudo (`self.xml`), no vuelve a pasar por el motor de escape de Jinja.

## Regla obligatoria: guardas `{% if %}` en todo campo nullable

Confirmado por render real: un campo `None` pasado a un tag `{{ }}` imprime literalmente la palabra `None` en el `.docx` (ej. `years_experience: null` → `"None+ YRS. OF EXP."`). **Todo campo que el schema marca `["string", "null"]` necesita guarda explícita**, nunca un tag directo:

```jinja
{% if years_experience %}{{ years_experience }}+ YRS. OF EXP.{% endif %}
```

**Bug corregido (30 jul 2026, hallado en auditoría de Opus):** la primera versión de este tag dejaba `+ YRS. OF EXP.` fuera del `{% endif %}` — con `years_experience: null` imprimía un `"+ YRS. OF EXP."` huérfano, y como `cv-schema.json` describía el campo con el `+` ya incluido (ej. `"8+"`), el render real producía `"8++ YRS. OF EXP."` (doble `+`). Corregido en dos lugares: el `.docx` ahora envuelve todo el texto literal dentro del `{% if %}` (mismo patrón que `town` en BD Format, que si desaparece por completo cuando es null), y `cv-schema.json` ahora especifica que `years_experience` va **sin** el `+` (el template lo agrega). Con `null`, el párrafo entero queda vacío — igual que cualquier otro guard de este documento.

Campos nullable en `cv-schema.json`: `town`, `years_experience`, `experience[].location`, `education[].period`.

## Regla de bloques multilínea (`{{r }}`)

Un `{% for %}{{ }}{% endfor %}` normal en `docxtpl` no genera salto de línea entre iteraciones — todo queda en el mismo párrafo, pegado. La solución validada:

1. En Python, se construye un objeto `RichText()` iterando la lista del JSON.
2. Entre cada línea/ítem se inserta un salto manual: `rt.xml += "<w:r><w:br/></w:r>"` (la clase `RichText` no tiene un método `.break()` — hay que tocar `.xml` directamente).
3. Cada ítem de una lista con "viñeta" (bullets, certifications, skills) se prefija manualmente con `"• "` (U+2022 + espacio) en el string, **no** se escribe el carácter en Word ni existe numeración nativa (`w:numPr`) en ninguno de los 3 templates — se verificó inspeccionando el XML de los `.docx` en `anotados/`.
4. El resultado completo del bloque se pasa como **una única variable** al contexto: `{"experience_block": rt, ...}`, y en el `.docx` va **un solo tag** `{{r experience_block }}`.

Ejemplo de construcción (experience):

```python
from docxtpl import RichText

rt = RichText()
for i, x in enumerate(experience):
    if i > 0:
        rt.xml += "<w:r><w:br/></w:r>"
    header = f"{x['title']} — {x['company']}"
    if x.get("location"):
        header += f", {x['location']}"
    header += f" ({x['period']})"
    rt.add(header, bold=True)
    for b in x["bullets"]:
        rt.xml += "<w:r><w:br/></w:r>"
        rt.add("• " + b)
```

Mismo patrón para `education_block`, `certifications_block`, `skills_block` (sin el header en negrita, solo `"• " + item` con `<w:br/>` entre ítems; el primer ítem no lleva salto previo).

## Sangría francesa (hanging indent) — se fija en el `.docx`, no en el render

`RichText` solo controla runs (texto), nunca las propiedades de párrafo (`pPr`) — el `<w:ind>` de sangría **no se puede setear desde Python en el momento del render**. Se fija **una sola vez, en Fase 2**, directamente en el párrafo contenedor de cada bloque (`experience_block`, `education_block`, `certifications_block`, `skills_block`) al re-anotar el `.docx`:

- Valor validado por spike: `left_indent = 0.25"`, `first_line_indent = -0.25"` (equivalente XML: `<w:ind w:left="360" w:hanging="360"/>`, en twips).
- Confirmado por render real que esta sangría **sobrevive intacta** el render de `docxtpl` (el motor solo reemplaza el contenido de los runs marcados, no toca `pPr`) y se aplica de forma uniforme a todas las líneas del párrafo, sean saltos de línea naturales (word-wrap) o `<w:br/>` manuales — esto es comportamiento estándar de OOXML, no específico de `docxtpl`.
- **Pendiente:** confirmación visual en Word/Paola una vez re-anotados los 3 templates reales (Fase 2) — el spike valida la estructura XML, no la apariencia final en pantalla.

## Ciclo de vida de `DocxTemplate` — una instancia por request

Confirmado en la auditoría: cachear el objeto `DocxTemplate` entre requests arriesga mezclar datos de candidatos distintos. El microservicio debe instanciar `DocxTemplate(template_path)` de cero en cada request, nunca reutilizar ni cachear a nivel de módulo/proceso.

## `Content-Disposition` con nombres no-ASCII

Confirmado que un `full_name` con caracteres no-ASCII (ej. "José Ramón Martínez Rodríguez") se renderiza perfecto **dentro** del `.docx` — el problema es exclusivo del header HTTP de descarga. El microservicio debe generar el nombre de archivo de descarga con codificación RFC 5987 (`Content-Disposition: attachment; filename="fallback-ascii.docx"; filename*=UTF-8''nombre-real-encoded.docx`), nunca interpolar el nombre no-ASCII directo en `filename=`.

---

## Regla de negocio (11 ago 2026): bullets, header de experiencia y estructura por formato

Confirmado por Paola vía 6 CVs canon (2 por formato, en `02-modulo2-agente-transformacion/cvs-canon/`) — reemplaza el diseño original de `{{r }}` con `RichText` descripto más abajo, que en la implementación final terminó resuelto con **loops nativos de Jinja a nivel de párrafo** (`{% for %}...{% endfor %}`, cada tag en su propio párrafo del `.docx`): `docxtpl` sí repite correctamente el párrafo por cada iteración cuando el loop vive a nivel de párrafo completo (a diferencia de un loop inline dentro de un mismo párrafo, que es el caso que el spike original de `RichText` estaba evitando). La sangría francesa y los tab stops sí sobreviven el render igual, sean párrafos repetidos por Jinja o `RichText`.

**Bullet por formato** (confirmado por extracción raw a nivel de carácter de los PDF canon, no solo visual):
- **New Format:** viñeta nativa de Word (`w:numPr`), fuente `Wingdings`, carácter `U+F02D` — implementada como definición de numeración propia (`numId` dedicado) en `templates/anotados/New Format Resume Template.docx`, nunca como texto literal.
- **Non Template:** guion simple `"- "` como texto literal (default elegido por Santiago; los 2 ejemplos de Paola no coincidían entre sí — Aneira usaba `"-"`, Andrea `"−"` más largo — y "Non Template" implica menor estandarización).
- **BD Format:** guion simple `"- "` como texto literal (confirmado por los 2 ejemplos, consistente).

**Header de experiencia — patrón universal, agrupado por empresa (los 3 formatos):** cada bloque de experiencia va en 2 líneas, no 1:
1. Línea de empresa (negrita, con tab stop derecho a 6.5"): `"{{ company.header }}"` = `"{empresa}[, {location}]"` + `"\t"` + período **solo si hay dato** (nunca imprime un tab colgante ni `"None"`).
2. Línea de rol (negrita, sin tab stop) por cada rol agrupado bajo esa empresa: `"{{ role.header }}"` = `"{title}"`, o `"{title} ({period})"` cuando hay 2+ roles agrupados (el período individual del rol solo se muestra ahí, nunca en la línea de empresa si hay un solo rol).

Cuando un candidato tuvo 2+ roles consecutivos en la misma empresa sin haberse ido entremedio (caso real: Edgeliz Ramos Rosario en Fresenius Kabi, canon BD), se agrupan en un solo bloque: la línea de empresa lleva el período **total** (inicio más temprano, fin más tardío, texto crudo preservado — ver `dates.combine_periods`), y cada rol lleva su propio período entre paréntesis. Empresas no consecutivas (el candidato volvió después de trabajar en otro lado) nunca se agrupan — son bloques separados aunque el nombre de empresa coincida.

Esto lo arma `blocks.build_experience_companies()` en Python (nunca en el `.docx` ni por el LLM) — devuelve `experience_companies: [{header, roles: [{header, bullets}]}]`, reemplazando el `experience_jobs` plano original.

`experience[].period` es **nullable** desde el 11 ago 2026 (antes era obligatorio) — CVs reales sin fechas para un proyecto/pasantía (caso real: Edward Cruz Vega, canon BD, 4 de sus experiencias sin fecha en el original) no deben forzar al agente a inventar una. `grounding.py` ya degradaba esto a warning (`EMPTY_PERIOD`), no a error, antes de este cambio — el ajuste fue solo de schema/prompt, no de lógica de grounding.

## Tabla de tags — New Format Resume Template.docx

| Sección | Tag |
|---|---|
| Header — nombre | `{{ full_name }}` |
| Header — años de experiencia | `{% if years_experience %}{{ years_experience }}+ YRS. OF EXP.{% endif %}` |
| EDUCATION | `{% for item in education_items %}` / `{{ item }}` (viñeta nativa) / `{% endfor %}` |
| SUMMARY OF QUALIFICATIONS | `{{ summary }}` |
| PROFESSIONAL EXPERIENCE | `{% for company in experience_companies %}` → `{{ company.header }}` → `{% for role in company.roles %}` → `{{ role.header }}` → `{% for b in role.bullets %}` → `{{ b }}` (viñeta nativa) → 3x `{% endfor %}` |
| SKILLS | `{% for item in skills_items %}` / `{{ item }}` (viñeta nativa) / `{% endfor %}` — **va antes** de certificaciones (orden confirmado por canon Kenneth/Yanina, invierte el orden original) |
| CERTIFICATIONS & TRAININGS | `{% for item in certifications_items %}` / `{{ item }}` (viñeta nativa) / `{% endfor %}` — título renombrado (antes tenía un typo: "LINCENSES, TRAININGS & CERTIFICATIONS") |
| Footer | `{{ full_name }}` |

**No implementado en esta ronda (decisión explícita de Santiago):** `CORE COMPETENCIES` antes de la experiencia y `TECHNICAL & PROFESSIONAL SKILLS` con subtítulos en negrita por categoría, ambos presentes en el canon de Kenneth pero no en el de Yanina — se adoptó la estructura de Yanina (más simple, sin esas 2 secciones) como estándar único de New Format. Tampoco se implementa partir la experiencia en una sección `ADDITIONAL EXPERIENCE` (presente en el canon de Yanina) — decisión explícita: nunca partir automáticamente, todo va en `PROFESSIONAL EXPERIENCE`.

## Tabla de tags — Non Template Resume.docx

Mismo mapeo de estructura fija que New Format (EDUCATION → SUMMARY OF QUALIFICATIONS → PROFESSIONAL EXPERIENCE → LICENSES, TRAININGS & CERTIFICATIONS → SKILLS), **sin reordenar ni renombrar secciones** — a diferencia de New Format, aquí no se tocó el orden/título de certificaciones ni skills. Único cambio: header de experiencia en 2 líneas agrupado por empresa (igual que los otros 2 formatos) y bullet `"- "` en vez de `"• "`.

**Hallazgo importante, no resuelto en esta ronda:** los 2 ejemplos canon de Paola (Aneira, Andrea) tienen secciones completamente distintas entre sí y distintas de esta estructura fija (`TECHNICAL SKILLS`/`PROFESSIONAL SKILLS`/`LANGUAGES`/`CERTIFICATIONS & RELEVANT COURSEWORK` en uno, `EXTRACURRICULAR ACTIVITIES`/`RELEVANT PROJECTS`/`SOFT SKILLS` en el otro) — sugiere que "Non Template" podría significar secciones variables por candidato (reflejando el CV original), no un template fijo con tags predefinidos. Decisión explícita de Santiago (11 ago 2026): mantener el template fijo actual por ahora; confirmar con Paola antes de rearquitecturar esto a render dinámico de secciones (cambio de arquitectura más grande, fuera de alcance de esta ronda).

## Tabla de tags — BD - Resume Template.docx

| Sección | Tag |
|---|---|
| Header — nombre | `{{ full_name }}` |
| Header — localidad | `{% if town %}{{ town }}{% endif %}` (línea propia debajo del nombre — **nunca** dentro del summary) |
| Summary of Skills: | `{{ summary }}` — párrafo corrido, sin bullets (se quitó la lista de skills que fusionaba antes; BD no renderiza `skills[]`) |
| Professional Experience: | mismo patrón de 3 niveles que New Format/Non Template (`experience_companies` → `roles` → `bullets`), bullet `"- "` |
| Education/Certifications/Licenses | `{% for item in education_certifications_items %}` / `- {{ item }}` / `{% endfor %}` |

Cambios de esta ronda vs. el diseño original:
- **Localidad:** ya vivía como línea propia bajo el nombre en el `.docx` (el diseño original de este documento describía mal el comportamiento real). Lo que sí se quitó fue la frase redundante `"Resides in {{ town }}."` que aparecía **además**, dentro de `Summary of Skills` — el canon nunca la muestra.
- **Skills:** se eliminó por completo de BD Format. Ningún ejemplo canon muestra una lista de skills con viñetas; `cv.skills` sigue existiendo en el JSON (se sigue extrayendo, por si se necesita en Módulo 3), pero `blocks.build_bd_format_context()` ya no lo pasa al contexto de render.
- **Títulos:** `"Summary of Skills"` → `"Summary of Skills:"`, `"Professional Experience"` → `"Professional Experience:"` (dos puntos, confirmado por los 2 ejemplos canon). `"Education/Certifications/Licenses"` se mantiene sin dos puntos (tampoco los tiene en el canon).

---

## Evidencia del spike (28 jul 2026)

Render real ejecutado contra una copia de `New Format Resume Template.docx` con un tag `{{r experience_block }}` y sangría francesa de 0.25" aplicada al párrafo, usando datos adversariales (`Johnson & Johnson`, `R&D`, `>8%`, `<2%`, comillas, nombre no-ASCII). Resultado verificado a nivel XML:

- `&`, `<`, `>`, comillas y acentos sobreviven intactos (`autoescape=True`).
- 5 elementos `<w:br/>` insertados correctamente para 2 experiencias / 4 líneas totales.
- `<w:ind w:left="360" w:hanging="360"/>` presente sin alteración tras el render.
- `{{ years_experience }}` con valor `null` confirmado que imprime `"None"` literal — motiva la guarda `{% if %}` obligatoria de este documento.
- Loop vacío (`education: []`) no rompe el render — se confirmó `{{r }}` con `RichText("")` (bloque vacío) también renderiza sin error.

Script y `.docx` de prueba en `/private/tmp/claude-501/.../scratchpad/spike/` (no versionado — son artefactos de spike, no fixtures del proyecto; los fixtures reales están en `02-modulo2-agente-transformacion/contrato-datos/fixtures/`).
