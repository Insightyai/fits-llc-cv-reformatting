---
name: prompt-optimizer
description: >-
  Analiza prompts para LLMs (GPT-4o, Claude), identifica debilidades y produce
  una versión optimizada lista para usar. Usar cuando se diseñen prompts para
  clasificación de marcas (Cuesta-Lawyers), scoring de CVs (Fits-LLC), o cualquier
  integración LLM en proyectos Insighty. Advisory only — no ejecuta la tarea.
origin: ecc-source (adapted for Insighty AI)
---

# Prompt Optimizer

Analiza un prompt draft, lo critica y produce una versión optimizada lista para pegar y usar en producción.

## Cuándo Usar

- Diseñando prompts para clasificación OMPI de marcas (Cuesta-Lawyers / GPT-4o mini)
- Diseñando prompts de scoring de CVs farmacéuticos (Fits-LLC / LLM)
- Evaluando calidad de prompts existentes antes de lanzar a producción
- Cuando el LLM produce resultados inconsistentes o incorrectos
- Cuando se necesita reducir tokens sin perder calidad de output
- Antes de cualquier entrega que incluya un prompt como parte del entregable

## Solo Advisory — No ejecutar la tarea

Este skill produce un análisis + prompt optimizado. No ejecuta la tarea del prompt ni interactúa con APIs externas.

---

## Pipeline de Análisis (6 fases)

### Fase 0: Contexto del Proyecto

Detectar el proyecto y caso de uso:
1. ¿Es para Cuesta-Lawyers? → contexto legal, clasificación OMPI, NO dar opiniones legales
2. ¿Es para Fits-LLC? → scoring de CVs, industria farmacéutica, roles específicos (QA, Regulatory, Manufacturing, Sales, Scientific)
3. ¿Es para Somaflow? → wellness/bienestar, NO contexto clínico, personalización por tipo de sistema nervioso
4. ¿Es un prompt genérico? → analizar sin contexto cliente específico

### Fase 1: Detección de Intención

Clasificar el tipo de tarea LLM:

| Categoría | Ejemplo |
|-----------|---------|
| Clasificación | "Clasificar marca en clase OMPI según descripción" |
| Scoring/Ranking | "Evaluar CV contra descripción de puesto, puntaje 0-100" |
| Extracción | "Extraer campos estructurados de documento OCR" |
| Generación | "Generar mensaje de WhatsApp personalizado para usuario" |
| Resumen | "Resumir historial de interacciones de un candidato" |
| Validación | "Verificar si la descripción cumple requisitos mínimos para registro" |

### Fase 2: Evaluación de Scope

| Scope | Descripción | Estrategia |
|-------|-------------|-----------|
| SIMPLE | Una tarea clara, output estructurado | Prompt directo con ejemplos |
| MEDIO | Múltiples criterios de evaluación | Chain-of-thought, descomponer en pasos |
| COMPLEJO | Razonamiento multi-paso, decisiones | Structured outputs + few-shot examples |

### Fase 3: Diagnóstico de Debilidades

Revisar el prompt original contra estos criterios:

**CRÍTICO:**
- [ ] ¿El prompt puede generar outputs que parezcan opiniones legales/médicas cuando no deben? (Cuesta, Somaflow)
- [ ] ¿El output tiene formato definido? (JSON, structured output, etc.)
- [ ] ¿Hay ejemplos (few-shot) para tareas de clasificación/scoring?

**ALTO:**
- [ ] ¿La tarea está claramente delimitada? (¿qué SÍ y qué NO debe hacer el LLM?)
- [ ] ¿El prompt incluye el contexto necesario o asume conocimiento que el LLM no tiene?
- [ ] ¿Hay instrucciones sobre cómo manejar casos ambiguos o edge cases?
- [ ] ¿El prompt especifica el nivel de confianza o certeza esperado?

**MEDIO:**
- [ ] ¿El prompt usa el idioma correcto? (español para clientes colombianos/latinoamericanos)
- [ ] ¿El tone es apropiado para el caso de uso?
- [ ] ¿Hay instrucciones de longitud de respuesta?

### Fase 4: Detectar Contexto Faltante

Revisar si falta información crítica:

- [ ] **Rol del LLM** — ¿Se define explícitamente quién "es" el LLM? (ej: "Eres un asistente de pre-screening...")
- [ ] **Restricciones** — ¿Qué NO debe hacer? (ej: "No emitas opiniones legales", "No contactes al candidato")
- [ ] **Output format** — ¿Está especificado el formato exacto de respuesta? (JSON schema, campos requeridos)
- [ ] **Casos edge** — ¿Qué hacer con información incompleta, documentos ilegibles, candidatos que no califican?
- [ ] **Escala de scoring** — ¿Está definido qué significa cada rango? (ej: 0-40 no califica, 41-70 revisar, 71-100 recomendar)
- [ ] **Ejemplos** — Para clasificación y scoring, ¿hay al menos 2-3 ejemplos (few-shot)?

### Fase 5: Recomendaciones de Modelo

| Caso de uso | Modelo recomendado | Razón |
|-------------|-------------------|-------|
| Clasificación OMPI (Cuesta) | GPT-4o mini | Costo-efectivo para clasificación estructurada |
| Scoring CVs farmacéuticos (Fits) | GPT-4o o Claude Sonnet | Mejor razonamiento para evaluación compleja |
| Mensajes WhatsApp (Somaflow) | GPT-4o mini | Alta volumen, bajo costo |
| Extracción OCR (Cuesta) | GPT-4o | Mejor manejo de texto imperfecto de OCR |

---

## Output Format

### Sección 1: Diagnóstico del Prompt Original

**Fortalezas:** Lo que el prompt hace bien.

**Problemas:**

| Problema | Impacto | Fix sugerido |
|---------|--------|--------------|
| (problema) | (consecuencia) | (cómo corregir) |

**Riesgos específicos para Insighty:**
- (riesgos legales, de compliance, de experiencia de usuario)

### Sección 2: Prompt Optimizado

Presentar el prompt completo optimizado en un bloque de código listo para copiar. Incluir:
- Rol del LLM claramente definido
- Contexto necesario
- Instrucciones claras de qué hacer y qué NO hacer
- Output format especificado (preferiblemente JSON)
- Casos edge manejados
- Few-shot examples si aplica

### Sección 3: Métricas de Evaluación

Sugerir cómo medir si el prompt mejorado funciona:
- ¿Qué tests manuales correr? (5-10 casos de prueba)
- ¿Qué métricas capturar? (precision en clasificación, tiempo de respuesta, tasa de outputs inválidos)
- ¿Cuándo considerar que el prompt está "listo para producción"?

---

## Ejemplos de Prompts Optimizados por Cliente

### Cuesta-Lawyers — Clasificación OMPI

```
Eres un asistente de pre-clasificación de marcas para un estudio de abogados. 
Tu rol es SUGERIR (no decidir) la clase OMPI más probable para un producto/servicio 
basándote en su descripción.

IMPORTANTE:
- No emitas opiniones legales ni recomendaciones definitivas
- Tu output es un INSUMO para que un abogado tome la decisión final
- Si no tienes suficiente información, indica qué datos adicionales necesitas

Input:
- Nombre de marca: {nombre}
- Descripción del producto/servicio: {descripcion}

Output en JSON:
{
  "clase_principal": <número 1-45>,
  "descripcion_clase": "<descripción de la clase OMPI>",
  "confianza": <"alta"|"media"|"baja">,
  "clases_alternativas": [<número>, ...],
  "razon": "<explicación breve en 1-2 oraciones>",
  "informacion_faltante": "<si aplica, qué información ayudaría a mejorar la clasificación>"
}
```

### Fits-LLC — Scoring de CV Farmacéutico

```
Eres un asistente de pre-screening de candidatos para una empresa farmacéutica. 
Tu rol es evaluar CVs contra una descripción de puesto y generar un scorecard estructurado.

IMPORTANTE:
- No tomes decisiones de contratación — eso corresponde al reclutador
- Evalúa SOLO con base en los criterios del puesto, no en características personales
- Si el CV está incompleto, indica qué información falta

Puesto: {titulo_puesto}
Requisitos clave: {requisitos}
CV del candidato: {texto_cv}

Output en JSON:
{
  "puntaje_total": <0-100>,
  "nivel": <"no_califica"|"revisar"|"recomendar">,
  "criterios": [
    {
      "criterio": "<nombre del criterio>",
      "puntaje": <0-10>,
      "evidencia": "<cita del CV que justifica el puntaje>",
      "brecha": "<qué le falta si aplica>"
    }
  ],
  "fortalezas": ["<fortaleza 1>", ...],
  "brechas": ["<brecha 1>", ...],
  "informacion_faltante": "<si aplica>"
}

Criterios de puntuación:
- 0-40: No cumple requisitos mínimos
- 41-70: Cumple parcialmente, requiere revisión del reclutador
- 71-100: Cumple o supera requisitos, recomendar entrevista
```

---

**Recordar**: La calidad del prompt define directamente la calidad del producto entregado al cliente. Un prompt bien diseñado reduce costos de tokens, aumenta consistencia y minimiza el riesgo de outputs incorrectos o peligrosos.
