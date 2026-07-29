# Mapeo de Placeholders por Template

> **Superado por `TAG-CONTRACT.md` (28 jul 2026).** La sintaxis de este documento (`{% for %}{{ }}{% endfor %}` directo en el `.docx`) no es compatible con el render multilínea — ver auditoría en `Decisiones.md`. Queda como referencia histórica de qué campo va en qué sección; para la sintaxis real de los tags usar `TAG-CONTRACT.md`.
>
> Traduce el esquema canónico (`../contrato-datos/cv-schema.json`) a los tags Jinja/`docxtpl` que van dentro de cada `.docx`, según la anatomía documentada en `../../conocimiento/anatomia-templates.md`.
> Sintaxis: `{{ campo }}` para valores simples, `{% for x in lista %}...{% endfor %}` para listas. Ver `INSTRUCCIONES-ANOTACION.md` para cómo escribirlos en Word sin romperlos.

---

## New Format Resume Template.docx / Non Template Resume.docx

Comparten estructura (ver anatomía). Mismo mapeo para ambos.

| Párrafo original | Reemplazar por |
|---|---|
| `NAME ` | `{{ full_name }}` |
| `+ YRS. OF EXP.` | `{{ years_experience }}+ YRS. OF EXP.` |
| (párrafo vacío bajo `EDUCATION`) | `{% for e in education %}{{ e.degree }}, {{ e.institution }}{% if e.period %} ({{ e.period }}){% endif %}{% endfor %}` (un párrafo por iteración — ver nota de loop multilínea abajo) |
| (párrafo vacío bajo `SUMMARY OF QUALIFICATIONS`) | `{{ summary }}` |
| (párrafo vacío bajo `PROFESSIONAL EXPERIENCE`) | `{% for x in experience %}{{ x.title }} — {{ x.company }}{% if x.location %}, {{ x.location }}{% endif %} ({{ x.period }}){% for b in x.bullets %}{{ b }}{% endfor %}{% endfor %}` |
| (párrafo vacío bajo `LINCENSES, TRAININGS & CERTIFICATIONS` / `LICENSES, TRAININGS & CERTIFICATIONS`) | `{% for c in certifications %}{{ c }}{% endfor %}` |
| (párrafo vacío bajo `SKILLS`) | `{% for s in skills %}{{ s }}{% endfor %}` |

**New Format únicamente** — footer `Name`: `{{ full_name }}` (a confirmar con Paola si se mantiene el tagline "Engineering | Construction Management Solutions", ver anatomía).

---

## BD - Resume Template.docx

| Párrafo original | Reemplazar por |
|---|---|
| `CANDIDATE NAME` | `{{ full_name }}` |
| `CANDIDATE LOCATION` | `{{ town }}` |
| (párrafo vacío bajo `Summary of Skills`) | `{{ summary }}{% if town %} Resides in {{ town }}.{% endif %}{% for s in skills %} {{ s }}{% endfor %}` — **regla especial BD**: el pueblo va aquí, dentro de Summary of Skills, no como sección propia |
| (párrafo vacío bajo `Professional Experience`) | mismo patrón de loop que New Format/Non Template |
| (párrafo vacío bajo `Education/Certifications/Licenses`) | `{% for e in education %}{{ e.degree }}, {{ e.institution }}{% endfor %}{% for c in certifications %}{{ c }}{% endfor %}` — fusiona `education` y `certifications` en una sola sección |

---

## Worksense Template.docx — eliminado del repo (28 jul 2026)

Paola (FITS) decidió descartar este formato el 21 jul 2026 (ver `Decisiones.md`); el 28 jul 2026 Santiago eliminó el archivo del repo como limpieza, siguiendo esa decisión. Si FITS reactiva este formato en el futuro, hay que pedirle el `.docx` de nuevo a Paola/Jeremy y rehacer este mapeo. El layout era "label inline" (el tag pegado al label en el mismo párrafo, no en un párrafo separado) — se documentó en su momento en `../../conocimiento/anatomia-templates.md` antes de borrar el archivo.

---

## Nota sobre loops multilínea en docxtpl

Un `{% for %}` normal en `docxtpl` imprime todo dentro del mismo párrafo (sin saltos de línea entre iteraciones). Para que cada experiencia/educación/skill quede en su propia línea hace falta el patrón `{%tr for %}` (row de tabla) — que no aplica aquí porque no hay tablas — o el filtro `{{ x.title }}{{ "\n"|e }}` no funciona en Word porque un salto de línea real requiere un `<w:br/>`, que `docxtpl` soporta vía el objeto `RichText` o el filtro `subdoc`.

**Esto es un detalle de implementación del microservicio (Fase 2), no de la anotación en Word**: en la guía de anotación (0.3) el tag se escribe simple (`{{ summary }}`, `{% for x in experience %}...{% endfor %}`); el microservicio arma cada bullet/experiencia como un párrafo separado usando `docxtpl.RichText` o `subdoc()` al momento de renderizar. No se necesita ninguna sintaxis especial en el `.docx` para esto — se resuelve en Python.

## Pendiente antes de tocar los `.docx` reales

- Confirmar con Paola/Jeremy el tagline del footer de New Format y el criterio de cálculo de `years_experience` (ver `_meta.warnings` y anatomía).
- Validar este mapeo contra un CV de ejemplo ya convertido por FITS (aún pendiente, Paola se comprometió a enviarlos) antes de dar la guía de anotación como definitiva — es la única forma de confirmar que no falta ningún campo.
