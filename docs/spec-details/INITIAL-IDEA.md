# INITIAL-IDEA.md: Intelligent Multimodal RAG Platform

## 1. Descripción general

Plataforma web para consulta inteligente de documentos mixtos (PDF, Markdown, imágenes) mediante RAG multimodal con Gemini. El sistema indexa documentos localmente con ChromaDB y responde preguntas citando las fuentes relevantes.

Diseñada para ser evaluable con un solo `docker run -e GEMINI_API_KEY=...`, sin dependencias externas obligatorias.

## 2. Caso de uso

Análisis de informes técnicos o financieros: el usuario sube documentos, los indexa, y hace preguntas en lenguaje natural. El sistema responde con referencias a las secciones fuente.

## 3. Arquitectura

- **Frontend/Backend:** Un solo servicio FastAPI con UI en Jinja2. Sin Node.js.
- **Almacenamiento vectorial:** ChromaDB persistido en volumen Docker (`-v`).
- **IA/ML:** Gemini API via SDK `google-genai` (embeddings + generación).
- **CI/CD:** GitHub Actions → build → push a GHCR con tags `:latest` y `:SHA`.
- **Despliegue:** Cloud Run (imagen pública en GHCR).

## 4. Flujos principales

**Ingestión:**
`Subida de archivo` → `Extracción de texto/imágenes` → `Chunking` → `Embeddings (Gemini)` → `ChromaDB`

**Consulta RAG:**
`Pregunta` → `Búsqueda semántica (ChromaDB)` → `Contexto recuperado` → `Gemini genera respuesta` → `Respuesta + citas`

## 5. Stack tecnológico

| Capa | Tecnología |
|---|---|
| Runtime | Python 3.12, `uv` |
| API | FastAPI, Uvicorn |
| UI | Jinja2 templates |
| Vector store | ChromaDB (local, volumen Docker) |
| IA | `google-generativeai` SDK |
| Métricas | `prometheus-fastapi-instrumentator` |
| Lint | `ruff` |
| Tests | `pytest` |
| CI/CD | GitHub Actions |
| Registro | GHCR |
| Despliegue | Cloud Run |
| GCS | Opcional (sincronización de índice) |

## 6. Variables de entorno

| Variable | Obligatoria | Descripción |
|---|---|---|
| `GEMINI_API_KEY` | Sí | Clave de API de Gemini. Solo en runtime, nunca en la imagen. |
| `GCS_BUCKET` | No | Bucket GCS para sincronización opcional del índice. |

## 7. Cumplimiento de rúbrica

| Criterio | Pts | Estrategia |
|---|---|---|
| Arranca con un solo `docker run` | 6 | Imagen autocontenida; ChromaDB local por defecto; GCS no bloqueante. |
| IA funcional | 6 | RAG multimodal con Gemini SDK; retrieval semántico + generación con citas. |
| README claro + 1 ejemplo | 3 | README con comando exacto, volumen, y ejemplo de entrada/salida real. |
| Puntos extra | 5 | Dockerfile multi-stage + uv, GHCR, GitHub Actions (lint + SHA tag), ruff, pytest, /metrics. |