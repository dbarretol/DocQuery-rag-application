# TASKS.MD: Roadmap de Implementación (MVP Evaluable)

Este documento define los paquetes de trabajo sistemáticos para construir la plataforma RAG Multimodal, utilizando `uv` y PowerShell.

## Fase 1: Configuración del Entorno
- [ ] Inicializar entorno Python con `uv`.
- [ ] Estructurar carpetas (`app/backend`, `docs`).
- [ ] Configurar `.gitignore` y `.dockerignore`.
- [ ] `uv add --dev ruff`.
- [ ] Configurar `[tool.ruff]` en `pyproject.toml`.
- [ ] **Validación:** Verificar entorno virtual activo y ejecución de `ruff check .`.

## Fase 2: Backend Core (FastAPI & GCS Opcional)
- [ ] Configurar FastAPI y dependencias (`uv add fastapi uvicorn google-cloud-storage chromadb google-generativeai prometheus-fastapi-instrumentator`).
- [ ] Implementar stub del endpoint de consulta RAG (`POST /chat`) (lógica RAG en fase 3).
- [ ] Implementar servicios de subida/eliminación/listado de documentos.
- [ ] Implementar validación de bucket GCS (no bloqueante para el arranque).
- [ ] Implementar validación de tipos, tamaños y límites de carga.
- [ ] Implementar endpoint `/health`.
- [ ] Implementar endpoint `/metrics` usando `prometheus-fastapi-instrumentator`.
- [ ] Implementar readiness y liveness checks.
- [ ] **Validación:** Tests de integración para endpoints de GCS (ejecución solo en CI).

## Fase 3: Lógica RAG Multimodal & Persistencia
- [ ] **Refactorizar `intro_multimodal_rag_utils.py` para usar `google-generativeai` SDK.**
- [ ] Utilizar **ChromaDB** como almacén vectorial local persistente.
- [ ] Implementar sincronización ChromaDB <-> GCS (opcional, al inicio/final).
- [ ] **Pipeline de ingesta modular:**
  - [ ] Implementar extracción de contenido (PDF, Markdown, imágenes).
  - [ ] Implementar chunking configurable.
  - [ ] Implementar generación de descripciones (Gemini SDK).
  - [ ] Implementar generación de embeddings.
  - [ ] Implementar almacenamiento en ChromaDB.
- [ ] Implementar estados del documento (Uploaded, Processing, Indexed, Error).
- [ ] Implementar sincronización y reindexación manual.
- [ ] Implementar recuperación de fuentes (trazabilidad y metadatos).
- [ ] **Finalizar integración del endpoint de consulta RAG (`POST /chat`) con lógica RAG real.**
- [ ] **Validación:** Tests unitarios (mocking), verificación de persistencia local, verificación de trazabilidad.

## Fase 4: Frontend (Jinja2 Templates)
- [ ] Implementar UI con plantillas Jinja2 dentro de FastAPI.
- [ ] UI de configuración (Input de bucket GCS solamente).
- [ ] UI de Upload (drag & drop) integrado con API.
- [ ] Panel de gestión (listado, estado de indexación, borrar).
- [ ] Interfaz de chat (respuestas, citas, preguntas sugeridas).
- [ ] **Validación:** Pruebas manuales de flujo (carga, chat, sugerencias).

## Fase 5: Infraestructura, CI/CD y Despliegue
- [ ] Crear `Dockerfile` multi-stage.
- [ ] Crear workflow de GitHub Actions:
  - [ ] Paso de `ruff check .`.
  - [ ] Build/push a GHCR con tags `:latest` y `:${{ github.sha }}`.
- [ ] Configurar despliegue en Cloud Run.
- [ ] Gestionar secretos (variables de entorno).
- [ ] Configurar logging estructurado para Cloud Run.
- [ ] Definir IAM mínima (`roles/storage.admin`).
- [ ] Documentar despliegue en `README.md`.
- [ ] **Validación:** Verificación de logs en Cloud Run y ejecución desde imagen en entorno limpio.

## Fase 6: Validación y QA
- [ ] Tests unitarios (`pytest`) para pipeline de procesamiento.
- [ ] Medir tiempo de indexación para documentos de prueba.
- [ ] Medir latencia media de consulta.
- [ ] Verificar flujo completo de extremo a extremo.
- [ ] **Validación:** QA final de seguridad y rendimiento.

## Fase 7: Verificación de Rúbrica
- [ ] **Redactar README:** Incluir comando `docker run` (con `-v` para persistencia de ChromaDB), ejemplo de entrada/salida real, y aclaración de modos (local vs GCS).
- [ ] Verificar arranque con único comando `docker run`.
- [ ] Verificar inyección de API Keys vía variables de entorno.
- [ ] Verificar ejecución sin dependencias locales adicionales.
- [ ] Ejecutar prueba completa siguiendo únicamente el README (simulación de evaluación).
- [ ] **Validación:** Simulación de entorno limpio para evaluación del profesor.
