# Contrato de Servicios Tecnológicos — CV Reformatting Automatizado

> Transcripción del PDF firmado. Documento fuente: `Contrato CV Reformatting FITS LLC 29.06.26.pdf`
> Firmado: 3 de julio de 2026 (PandaDoc, Ref. UTPMD-5NM4I-BUYGT-KWFRW)

**Partes:** Insighty AI LLC (Proveedor, representada por Natalia García Pulido) y FITS LLC (Cliente, representada por Yaritza Cordero Nieves).

---

## Primero. Alcance de los Servicios

Sistema automatizado de reformateo de CV para FITS, compuesto por 3 módulos:

1. **Job Posting Centralizado "Resumes" en JazzHR** — configuración del job posting centralizado con 4 stages, uno por formato: New Format (logo FITS, SOW requisitions), Non Template (sin logo — Medtronic, Integra FG, Haleon FG, Beeline, Amgen FG, Abbott FG), BD Format (Becton Dickinson) y Worksense Format (Johnson & Johnson), con acceso habilitado para todos los reclutadores.
2. **Agente de Transformación AI** — workflow en N8N conectado al job posting "Resumes", agente AI vía Anthropic/Claude que aplica 4 reglas de contenido (traducción al inglés si el CV está en otro idioma, conversión a tercera persona, sustitución de Objectives por Summary profesional, reescritura de summaries pobres/incompletos), y generación programática del .docx final con los 4 templates (logo, estilos de fuente, orden de secciones por formato — incluyendo pueblo de residencia en Summary of Skills para BD Format).
3. **Entrega al Equipo** — generación del CV transformado en .docx editable, almacenamiento automático en Google Drive de FITS por defecto (integración con OneDrive vía Microsoft Graph API activada una vez que TI de FITS habilite el acceso, sin costo adicional y sin afectar la fecha de entrega), email automático al correo grupal del equipo con el CV adjunto y enlace directo, entregado en menos de 5 minutos desde el trigger.

### Criterios de Aceptación por Módulo (binarios: Cumple/No Cumple)

- **Módulo 1:** (a) el job posting "Resumes" está activo en JazzHR con 4 stages correctamente nombrados. (b) todos los reclutadores tienen acceso confirmado por el representante designado del cliente.
- **Módulo 2:** (a) el agente procesa un CV de prueba en menos de 3 minutos desde el trigger hasta el output en .docx. (b) las reglas de formato (traducción, tercera persona, sustitución Objectives/Summary) se aplican en el 100% del set de prueba acordado (15–20 CVs reales provistos por FITS en el kick-off). (c) la calidad de reescritura del Summary es aprobada por FITS en ≥90% del set de prueba. (d) el template correcto se aplica para cada uno de los 4 formatos.
- **Módulo 3:** (a) el .docx se almacena en la carpeta de Drive designada dentro de 5 minutos del trigger. (b) el correo grupal recibe el email con el CV adjunto y enlace funcional. (c) el log de procesamiento en Google Sheets registra la entrada correctamente (candidato, formato, fecha, resultado).

---

## Segundo. Honorarios y Condiciones de Pago

**Valor total: USD 2,000.** Pagos:
- USD 1,000 a la firma del contrato — activa el desarrollo
- USD 1,000 a la firma del Acta de Aceptación Final de Módulos

Cualquier demora en el pago suspende automáticamente el trabajo, las obligaciones de entrega/soporte y los plazos, sin que constituya incumplimiento de Insighty. Pagos en USD vía transferencia bancaria o tarjeta (Stripe, 3% + tarifas a cargo del cliente).

---

## Tercero. Plazo

**3 a 4 semanas calendario**, contadas desde lo que ocurra después entre: (a) fecha en que Insighty recibe los 4 templates definitivos con branding, o (b) recepción del pago inicial. No excede **7 semanas calendario** desde el inicio, salvo demoras atribuibles al cliente, terceros, aprobaciones pendientes, accesos faltantes o cambios solicitados.

---

## Cuarto. Alcance — Inclusiones y Exclusiones

Todo el trabajo es remoto. **No incluido:**
- Desarrollo/soporte presencial
- Desarrollo de componentes fuera de los 3 módulos definidos
- Integración con sistemas externos no especificados
- Templates adicionales a los 4 formatos definidos (requieren orden de servicio separada)
- Evaluación de idoneidad del candidato (cubierta por el agente de screening de Fase 1)
- Entrega final del CV al cliente de FITS (sigue siendo del reclutador; este sistema entrega solo al equipo interno de FITS)
- Modificaciones a job postings activos existentes en JazzHR (solo el posting centralizado "Resumes" está en alcance)
- **CVs escaneados o en formato de imagen** (PDFs sin texto seleccionable) — excluidos del alcance, el agente requiere texto legible por máquina
- **Ajustes de prompt de AI para nuevos tipos/formatos de CV** no representados en el set de prueba de aceptación — constituyen nuevo alcance, se cotizan aparte
- Migración de datos históricos de sistemas legacy
- Auditorías de seguridad o certificaciones
- Adquisición/gestión de licencias de terceros

### Prerequisitos — condiciones bloqueantes antes de la firma (ya cumplidas al firmarse el contrato)

1. **Templates con branding completo:** los 4 templates en .docx con logo embebido y estilos de fuente aplicados, entregados por FITS antes de la firma. El plazo de 3–4 semanas corre desde la fecha en que Insighty recibe los 4 archivos definitivos, no desde la firma.
2. **Destino de entrega confirmado:** el sistema se entrega con Google Drive como destino por defecto. La integración con OneDrive (Microsoft Graph API vía Azure AD) se activa una vez que TI del cliente habilite el acceso, sin costo adicional y sin afectar la fecha de entrega. FITS confirmó la carpeta de Google Drive o el estado de configuración de OneDrive antes de la firma.

> **Nota de implementación (post-firma):** por recomendación de Insighty a Centeno (IT de FITS), este proyecto usará su **propio sitio de SharePoint con Document Library** (separado del de Contract Renewal) para los 4 templates y la entrega de CVs transformados, en vez de Google Drive/OneDrive personal — ver `Decisiones.md`. Esto no cambia el alcance funcional, cambia el mecanismo técnico de almacenamiento/entrega.

---

## Quinto–Octavo. Obligaciones, Propiedad Intelectual, Confidencialidad

Mismos términos que Contract Renewal: Insighty ejecuta conforme a estándares de calidad y confidencialidad, sin garantizar resultados de negocio específicos. FITS provee accesos y designa responsable de proyecto. Propiedad intelectual se transfiere a FITS tras pago total. Insighty es procesador de datos, FITS es responsable del tratamiento.

---

## Noveno. Garantía y Soporte

- **Garantía:** 30 días calendario desde la Fecha de Go-Live Final. Cubre defectos reproducibles dentro del alcance de los módulos contratados. No cubre infraestructura, cambios de API de terceros (Anthropic/Claude, JazzHR, Google Drive/Google APIs, Microsoft Graph API), ni funcionalidades fuera de alcance.
- **Mantenimiento correctivo:** hasta **5 horas** en el primer mes, para defectos de producción y correcciones a variables/campos/configuraciones existentes. No cubre nuevos templates/formatos, cambios en la lógica de transformación del agente (aunque se enmarquen como correcciones), ajustes de prompt por nuevos tipos de CV/idiomas/estructuras no cubiertos en el set de prueba, ajustes estéticos, ni errores de terceros — todo eso se cotiza como orden de cambio.

---

## Décimo. Implementación, Capacitación y Documentación

Mismos términos que Contract Renewal: Acta de Aceptación por módulo con 5 días hábiles para firma/rechazo (silencio = aceptación automática), máximo 2 rondas de feedback consolidado para interfaces visuales, modificaciones sustanciales requieren acuerdo formal por escrito, capacitación virtual incluida.

## Undécimo–Vigésimo (resumen)

Terminación anticipada con 15 días de aviso; limitación de responsabilidad al monto pagado; ley de Delaware con arbitraje AAA en inglés; contratista independiente. Anexo 1 (Propuesta Comercial — CV Reformatting Automatizado, Junio 2026) forma parte integral del contrato.

---

## Anexo 1 — Cronograma de referencia (3–4 semanas desde el kick-off)

| Semana | Actividad |
|---|---|
| 1 | Configuración job posting · Construcción programática de los 4 templates con branding real · Setup del workflow en N8N |
| 2 | Desarrollo del agente AI de transformación · Setup de entrega en Drive · Pruebas con CVs reales del equipo |
| 3 | Ajustes según feedback · Pruebas finales de ciclo completo · Entrega y documentación |

Las pruebas de aceptación se realizan sobre un set de 15–20 CVs reales acordado con FITS al inicio del proyecto.

**Stakeholders del lado FITS:** Yaritza Cordero Nieves (representante legal/firma), Jeremy Rivera, Paola Guirado (operación/entrega), Agustín, Centeno (IT).
