---
description: Revisar un workflow n8n contra el checklist de calidad de Insighty. Verifica error handling, idempotencia, rate limiting, credenciales hardcodeadas, y reglas específicas por cliente (ej: nunca radicación automática en Cuesta-Lawyers).
---

Invoca el agente `n8n-reviewer` para revisar el workflow n8n indicado.

Si el usuario no especificó un archivo o workflow específico, buscar en la carpeta del cliente activo archivos JSON de n8n o descripciones de flujos en documentos.

El agente debe:
1. Leer el workflow (JSON exportado de n8n o descripción en texto)
2. Aplicar el checklist completo del agente n8n-reviewer
3. Identificar el cliente al que corresponde (Somaflow, Cuesta-Lawyers, Fits-LLC) y aplicar reglas específicas
4. Presentar findings organizados por severidad (CRÍTICO, ALTO, MEDIO, BAJO)
5. Para cada finding CRÍTICO y ALTO, incluir el fix específico con ejemplo de nodo corregido

Usar el agente n8n-reviewer para el análisis completo.
