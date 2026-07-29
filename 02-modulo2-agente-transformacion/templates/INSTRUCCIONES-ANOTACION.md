# Guía para Anotar Templates con Placeholders

> Para Santiago. Objetivo: insertar los tags Jinja/`docxtpl` de `MAPEO-PLACEHOLDERS.md` dentro de los `.docx`, sin romper el branding y sin que Word "parta" un tag en varios runs de XML (el bug que hace fallar `docxtpl` en silencio — el archivo abre normal en Word pero el render falla o deja el tag sin reemplazar).

**Estado (28 jul 2026):** los 3 templates activos (`New Format`, `Non Template`, `BD Format`) ya están anotados y validados en `anotados/` — se hizo por script (más rápido y con verificación automática vía `docxtpl`) en vez de manualmente en Word. Esta guía queda como referencia por si en el futuro llega un template nuevo o hay que rehacer alguno a mano.

## Por qué no alcanza con escribir el tag a mano

Cuando escribes `{{ full_name }}` letra por letra, el corrector ortográfico, el autocompletado y el autocorrector de Word pueden interrumpir el run de texto a mitad de camino (por ejemplo al detectar "full_name" como error y sugerir una corrección, o al autocapitalizar después de un punto). El resultado: en el XML interno, `{{ full` queda en un run y `_name }}` en otro. Visualmente en Word se ve idéntico. En la práctica, `docxtpl` tolera bien este caso (tiene lógica propia para reconstruir tags partidos), pero de todas formas conviene evitarlo.

**La forma más segura es no escribir el tag directamente: usar Buscar y Reemplazar (Ctrl+H / Cmd+Shift+H en Mac).** Reemplazar no dispara autocorrección ni autocompletado, y conserva el tag como un único run.

**Cuidado con "conservar mayúsculas y minúsculas del texto original":** si el texto que buscas está en mayúsculas (ej. `NAME`) y escribes el reemplazo en minúsculas (`full_name`), Word por defecto vuelve a poner el reemplazo en mayúsculas para "coincidir" con el original. Si esto pasa, revisa las opciones del buscador (ícono de engranaje) y activa "Coincidir mayúsculas y minúsculas", o corrige manualmente seleccionando solo la parte en mayúsculas y retipeándola.

## Procedimiento general

1. Antes de empezar, copia el original a `templates/anotados/` con el mismo nombre. **Nunca edites el original en `templates/`.**
2. Abre la copia en Word (no Pages ni Google Docs — deben ser tags en runs de Word real, ya que el render final usa `docxtpl` sobre este mismo archivo).
3. Para los placeholders que **reemplazan un texto existente** (ej. `CANDIDATE NAME` → `{{ full_name }}`): abre Buscar y Reemplazar, pega el texto exacto a buscar, pega el tag exacto a reemplazar, click en "Reemplazar" (no "Reemplazar todos" — así controlas que sea la ocurrencia correcta).
4. Para los placeholders que van en un **párrafo vacío** (no hay texto para buscar): primero escribe un token simple sin espacios ni símbolos especiales en ese párrafo (ej. `TAGSUMMARY`), guarda, y recién ahí usa Buscar y Reemplazar para cambiar `TAGSUMMARY` por el tag Jinja completo. El token intermedio evita el problema por completo porque no tiene nada que el corrector quiera "arreglar".
5. Guarda como `.docx` (no cambies el formato).
6. Repite para cada tag de la tabla correspondiente más abajo.
7. Al terminar, avísame — corro una validación local (compilar el template con `docxtpl` contra datos de prueba) antes de que estos archivos anotados sean la fuente de verdad del microservicio.

## Antes de arrancar: desactivar autocorrección (por las dudas)

Aunque el método de Buscar y Reemplazar ya evita el problema, como precaución extra:
- **Word > Preferencias > Revisión > Autocorrección** (Mac) o **Archivo > Opciones > Revisión > Opciones de Autocorrección** (Windows): destilda "Reemplazar texto mientras escribe" y "Corregir dos mayúsculas iniciales seguidas".
- Desactiva el subrayado rojo de ortografía en esta sesión de edición si te resulta molesto (no es obligatorio si usas el método de Buscar y Reemplazar).

## Tabla 1 — New Format Resume Template.docx y Non Template Resume.docx

Mismo procedimiento en ambos archivos (comparten estructura, ver anatomía).

| Paso | Buscar | Reemplazar por (token intermedio → tag final) |
|---|---|---|
| Header cuerpo | `NAME ` (con el espacio final) | directo → `{{ full_name }}` |
| Header cuerpo | `+ YRS. OF EXP.` | directo → `{{ years_experience }}+ YRS. OF EXP.` |
| Párrafo vacío bajo `EDUCATION` | (escribir) `TAGEDU` | → `{% for e in education %}{{ e.degree }}, {{ e.institution }}{% if e.period %} ({{ e.period }}){% endif %}{% endfor %}` |
| Párrafo vacío bajo `SUMMARY OF QUALIFICATIONS` | (escribir) `TAGSUMMARY` | → `{{ summary }}` |
| Párrafo vacío bajo `PROFESSIONAL EXPERIENCE` | (escribir) `TAGEXP` | → `{% for x in experience %}{{ x.title }} — {{ x.company }}{% if x.location %}, {{ x.location }}{% endif %} ({{ x.period }}){% for b in x.bullets %}{{ b }}{% endfor %}{% endfor %}` |
| Párrafo vacío bajo `LINCENSES...` / `LICENSES...` | (escribir) `TAGCERT` | → `{% for c in certifications %}{{ c }}{% endfor %}` |
| Párrafo vacío bajo `SKILLS` | (escribir) `TAGSKILLS` | → `{% for s in skills %}{{ s }}{% endfor %}` |

**Solo en New Format** — pie de página: busca `Name` dentro del footer (cuidado: es una palabra corta, verifica que estás parado en el footer y no en el cuerpo) y reemplaza por `{{ full_name }}`.

## Tabla 2 — BD - Resume Template.docx

| Paso | Buscar | Reemplazar por |
|---|---|---|
| Header cuerpo | `CANDIDATE NAME` | → `{{ full_name }}` |
| Header cuerpo | `CANDIDATE LOCATION` | → `{{ town }}` |
| Párrafo vacío bajo `Summary of Skills` | (escribir) `TAGSUMMARY` | → `{{ summary }}{% if town %} Resides in {{ town }}.{% endif %}{% for s in skills %} {{ s }}{% endfor %}` |
| Párrafo vacío bajo `Professional Experience` | (escribir) `TAGEXP` | → `{% for x in experience %}{{ x.title }} — {{ x.company }}{% if x.location %}, {{ x.location }}{% endif %} ({{ x.period }}){% for b in x.bullets %}{{ b }}{% endfor %}{% endfor %}` |
| Párrafo vacío bajo `Education/Certifications/Licenses` | (escribir) `TAGEDU` | → `{% for e in education %}{{ e.degree }}, {{ e.institution }}{% endfor %}{% for c in certifications %}{{ c }}{% endfor %}` |

## Worksense Template.docx — eliminado del repo (28 jul 2026)

Paola (FITS) decidió descartar este formato el 21 jul 2026 (ver `Decisiones.md`); el 28 jul 2026 Santiago eliminó el archivo del repo como limpieza, siguiendo esa decisión. Si se reactiva el formato, hay que pedirle el `.docx` de nuevo a FITS antes de anotarlo.

## Checklist final antes de avisarme

- [ ] Los archivos originales en `templates/` quedaron intactos.
- [ ] Las copias anotadas están en `templates/anotados/` con el mismo nombre de archivo.
- [ ] Ningún `TAGxxx` intermedio quedó sin reemplazar (Ctrl+F rápido por "TAG" en cada archivo para confirmar cero resultados).
- [ ] El logo y el branding siguen visibles igual que en el original (New Format y BD Format).
