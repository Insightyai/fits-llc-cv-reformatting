---
description: Analizar y optimizar un prompt para LLM (GPT-4o, Claude). Usar cuando se diseñen prompts para clasificación de marcas OMPI (Cuesta-Lawyers), scoring de CVs farmacéuticos (Fits-LLC), mensajes WhatsApp (Somaflow), o cualquier integración LLM. Produce diagnóstico + prompt optimizado listo para usar.
---

Usa la skill `prompt-optimizer` para analizar el prompt proporcionado.

Si el usuario proporcionó un prompt, analizarlo directamente.
Si no, pedir que comparta el prompt a optimizar y el caso de uso (cliente + tarea).

La skill debe:
1. Detectar el proyecto/cliente y caso de uso (Cuesta-Lawyers, Fits-LLC, Somaflow, u otro)
2. Clasificar la tarea LLM (clasificación, scoring, extracción, generación, etc.)
3. Diagnosticar debilidades del prompt original con tabla de problemas e impactos
4. Identificar contexto faltante (restricciones, output format, casos edge, few-shot examples)
5. Producir el prompt optimizado completo, listo para copiar y usar
6. Sugerir métricas para evaluar si el prompt mejorado funciona en producción

Incluir advertencias específicas si el prompt podría generar outputs que parezcan opiniones legales (Cuesta) o médicas/clínicas (Somaflow).
