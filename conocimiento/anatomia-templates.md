# Anatomía de los 4 Templates .docx

> Generado inspeccionando el XML interno (`word/document.xml`, `header1.xml`, `footer1.xml`) de los 4 `.docx` en `../02-modulo2-agente-transformacion/templates/`, vía `unzip` + `python-docx` + `pandoc`. Base para el esquema de datos (0.2) y la guía de anotación (0.3).

Los 4 son documentos de **una sola columna**, sin tablas ni cuadros de texto (`w:tbl`, `w:txbxContent`, `w:drawing` en el cuerpo: 0 en los 4). Cada sección es un encabezado en negrita seguido de párrafos vacíos donde va el contenido — no hay contenido de ejemplo ni placeholders `{{ }}` todavía.

---

## New Format Resume Template.docx

**Uso:** etapa "Convert Resume - New Format" (JNJ, SOW, Haleon FG, JazzHR Standard). Con logo.

- **Header** (se repite en cada página, imagen `image1.jpeg` = logo FITS): dirección, teléfono, email, web con hyperlinks (`fits.llc@fitspr.com`, `www.fitspr.com`).
- **Footer:** `Name` · `Page 1 of 1` · `Engineering | Construction Management Solutions`.
  - ⚠️ El tagline "Engineering | Construction Management Solutions" no corresponde a un cliente farmacéutico — parece residuo de un template genérico de otra industria. Confirmar con Paola/Jeremy si se debe reemplazar o eliminar (no es una regla de contenido documentada en el PRD).
  - El footer dice literalmente `Name` — es candidato a placeholder (nombre del candidato repetido en el pie de página), a confirmar en la guía de anotación.
- **Cuerpo** (fuente Arial, encabezados 10pt bold con borde inferior):

| Párrafo | Texto | Rol |
|---|---|---|
| 0 | `NAME ` | Placeholder — nombre del candidato |
| 1 | `+ YRS. OF EXP.` | Placeholder — años de experiencia (formato "N+ YRS. OF EXP.") |
| 2–4 | (vacíos) | — |
| 5 | `EDUCATION` | Encabezado sección |
| 6–7 | (vacíos) | Contenido de educación |
| 8 | `SUMMARY OF QUALIFICATIONS` | Encabezado sección |
| 9–10 | (vacíos) | Contenido del summary |
| 11 | `PROFESSIONAL EXPERIENCE` | Encabezado sección |
| 12–13 | (vacíos) | Contenido de experiencia |
| 14 | `LINCENSES, TRAININGS & CERTIFICATIONS` | Encabezado sección (typo "LINCENSES" en el original — no corregir sin confirmar con FITS) |
| 15–17 | (vacíos) | Contenido de certificaciones |
| 18 | `SKILLS` | Encabezado sección |
| 19–20 | (vacíos) | Contenido de skills |

**Orden de secciones:** Nombre/Años exp → Education → Summary → Professional Experience → Licenses/Certs → Skills.

---

## Non Template Resume.docx

**Uso:** etapa "Convert Resume - Non Template" (Abbott FG, Amgen FG, Beeline, Haleon FG, JazzHR Standard, JNJ, Integra FG, Medtronic). Sin logo, sin header ni footer.

Estructura del cuerpo **idéntica** a New Format (mismos 21 párrafos, mismo orden de secciones, mismos estilos Arial/10pt/bold+borde), salvo:
- Sin header/footer (no hay logo ni dirección de FITS).
- Único typo distinto: dice `LICENSES, TRAININGS & CERTIFICATIONS` (correctamente escrito, a diferencia de New Format).

Esto simplifica el mapeo: **New Format y Non Template comparten el mismo esquema de placeholders**; solo cambia la presencia de header/footer con logo.

---

## BD - Resume Template.docx

**Uso:** etapa "Convert Resume - BD Format" (Becton Dickinson). Con logo (2 imágenes en el header: `image1.jpg`, `image2.png` — confirmar con Paola cuál es el logo FITS y cuál es específico de BD).

- **Header:** vacío (el logo va como imagen flotante, no como texto).
- **Footer:** vacío.
- **Cuerpo** (32 párrafos, sin bordes bajo los encabezados vistos en el XML — mismo estilo Normal para todo):

| Párrafo | Texto | Rol |
|---|---|---|
| 0 | `CANDIDATE NAME` | Placeholder — nombre del candidato |
| 1 | `CANDIDATE LOCATION` | Placeholder — pueblo de residencia (ver regla especial BD, Módulo 2 README) |
| 2 | (vacío) | — |
| 3 | `Summary of Skills` | Encabezado sección — **aquí se inserta el pueblo de residencia según la regla de negocio de BD Format** |
| 4–8 | (vacíos) | Contenido de skills/summary |
| 9 | `Professional Experience` | Encabezado sección |
| 10–24 | (vacíos, 15 párrafos) | Contenido de experiencia — el bloque más largo, consistente con listar varias posiciones |
| 25 | `Education/Certifications/Licenses` | Encabezado sección |
| 26–31 | (vacíos) | Contenido de educación/certificaciones |

**Orden de secciones:** Nombre/Ubicación → Summary of Skills (incluye pueblo) → Professional Experience → Education/Certifications/Licenses.

**Diferencia clave vs. New Format/Non Template:** no tiene sección "SKILLS" separada — está fusionada en "Summary of Skills" junto con el pueblo de residencia. Confirma por qué la regla especial de BD vive en el template (D2 del plan), no en el prompt.

---

## Worksense Template.docx

**Uso:** ninguno activo (descartado, ver `../Decisiones.md`). Sin logo, sin header/footer. Se documenta y anota igual, por si se reevalúa (R3 del plan — riesgo del criterio contractual "4 formatos").

| Párrafo | Texto | Rol |
|---|---|---|
| 0 | `Name NAME` | Label "Name" + placeholder bold `NAME` |
| 1 | `Johnson & Johnson Previous experience (contract or FTE): ` | Label específico de JNJ — placeholder al final de la línea |
| 2–3 | (vacíos) | — |
| 4 | `Recruiter's comments/ Summary: ` | Encabezado — placeholder al final |
| 5–6 | (vacíos, estilo `Default` en 5) | Contenido |
| 7 | `Skills:` | Encabezado |
| 8–9 | (vacíos) | Contenido |
| 10 | `Education/ Certification/ Training: ___________` | Encabezado con línea de subrayado literal (no es un campo de formulario) |
| 11–12 | (vacíos) | Contenido |
| 13 | `Experience:` | Encabezado |
| 14–15 | (vacíos) | Contenido |

Nota: este template usa formato "Label: valor" en la misma línea (no heading + párrafo vacío como los otros 3) — el placeholder debe ir *dentro* del mismo párrafo del label, no en uno separado.

---

## Conclusión para el esquema de datos (0.2)

- **New Format y Non Template** comparten estructura 1:1 → mismo mapeo de tags.
- **BD Format** fusiona Skills+Summary+pueblo en una sola sección y no tiene sección Skills separada.
- **Worksense** usa un layout "label inline" distinto a los otros 3.
- Los 4 templates no tienen contenido de ejemplo ni tablas — toda la lista de experiencia/educación se escribe como texto plano dentro del bloque vacío bajo cada encabezado, lo que confirma que `docxtpl` necesita un tag con loop Jinja (`{% for exp in experience %}`) dentro de ese bloque, no celdas de tabla repetidas.
