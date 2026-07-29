# Contrato de Tags — Microservicio de Render

> Especificación definitiva de los tags Jinja2/`docxtpl` para los 3 templates activos (New Format, Non Template, BD Format). Reemplaza los tags de `MAPEO-PLACEHOLDERS.md` y de los `.docx` en `anotados/` (anotados el 28 jul con tags simples `{{ }}`) — ambos quedan como referencia histórica, no como fuente de verdad. Los `.docx` reales se re-anotan en Fase 2 siguiendo este documento.
>
> **Motivo del reemplazo:** la auditoría de Opus (28 jul 2026, ver `Decisiones.md` y `seguimiento/bitacora.md`) encontró que los tags simples `{{ for %}{{ }}{% endfor %}` no son compatibles con la técnica de render multilínea (`RichText`) — generan un párrafo vacío sin error, o concatenan todo el contenido en una sola línea sin separación. Este documento fue validado con renders reales (`docxtpl` 0.20.2) antes de escribirse — ver evidencia al final.

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
{% if years_experience %}{{ years_experience }}{% endif %}+ YRS. OF EXP.
```

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

## Tabla de tags — New Format Resume Template.docx / Non Template Resume.docx

Comparten estructura (ver `conocimiento/anatomia-templates.md`). Mismo mapeo para ambos.

| Sección | Tag |
|---|---|
| Header — nombre | `{{ full_name }}` |
| Header — años de experiencia | `{% if years_experience %}{{ years_experience }}{% endif %}+ YRS. OF EXP.` |
| EDUCATION | `{{r education_block }}` |
| SUMMARY OF QUALIFICATIONS | `{{ summary }}` |
| PROFESSIONAL EXPERIENCE | `{{r experience_block }}` |
| LICENSES, TRAININGS & CERTIFICATIONS | `{{r certifications_block }}` |
| SKILLS | `{{r skills_block }}` |
| Footer (solo New Format) | `{{ full_name }}` |

`education_block`: por ítem, `"{{ degree }}, {{ institution }}"` + `" ({{ period }})"` si `period` no es null; `<w:br/>` entre ítems.
`certifications_block` / `skills_block`: por ítem, `"• " + valor`; `<w:br/>` entre ítems.

## Tabla de tags — BD - Resume Template.docx

| Sección | Tag |
|---|---|
| Header — nombre | `{{ full_name }}` |
| Header — localidad | `{% if town %}{{ town }}{% endif %}` |
| Summary of Skills | `{{r summary_skills_block }}` |
| Professional Experience | `{{r experience_block }}` (mismo patrón que New Format/Non Template) |
| Education/Certifications/Licenses | `{{r education_certifications_block }}` |

`summary_skills_block` fusiona `summary` + regla especial BD (`town` dentro de esta sección, no en sección propia) + `skills`: párrafo de summary sin viñeta, seguido de `"Resides in {{ town }}."` si `town` no es null, seguido de cada skill con `"• "` y `<w:br/>`.

`education_certifications_block` fusiona `education[]` + `certifications[]` en un solo bloque (mismo formato de ítem que `education_block`, seguido de los ítems de `certifications_block`).

**Abierto para Fase 2 (no bloqueante):** `summary_skills_block` mezcla texto corrido (summary, sin viñeta) con una lista con viñeta (skills) dentro del mismo párrafo — la sangría francesa uniforme del párrafo podría verse rara aplicada al summary. Confirmar visualmente con Paola al re-anotar; si no convence, separar en dos tags/párrafos (`{{r summary_block }}` + `{{r skills_block }}`) en vez de fusionarlos en uno.

---

## Evidencia del spike (28 jul 2026)

Render real ejecutado contra una copia de `New Format Resume Template.docx` con un tag `{{r experience_block }}` y sangría francesa de 0.25" aplicada al párrafo, usando datos adversariales (`Johnson & Johnson`, `R&D`, `>8%`, `<2%`, comillas, nombre no-ASCII). Resultado verificado a nivel XML:

- `&`, `<`, `>`, comillas y acentos sobreviven intactos (`autoescape=True`).
- 5 elementos `<w:br/>` insertados correctamente para 2 experiencias / 4 líneas totales.
- `<w:ind w:left="360" w:hanging="360"/>` presente sin alteración tras el render.
- `{{ years_experience }}` con valor `null` confirmado que imprime `"None"` literal — motiva la guarda `{% if %}` obligatoria de este documento.
- Loop vacío (`education: []`) no rompe el render — se confirmó `{{r }}` con `RichText("")` (bloque vacío) también renderiza sin error.

Script y `.docx` de prueba en `/private/tmp/claude-501/.../scratchpad/spike/` (no versionado — son artefactos de spike, no fixtures del proyecto; los fixtures reales están en `02-modulo2-agente-transformacion/contrato-datos/fixtures/`).
