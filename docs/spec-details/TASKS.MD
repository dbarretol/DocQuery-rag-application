# TASKS.MD: Roadmap de Implementación (MVP Evaluable)

Este documento define los paquetes de trabajo sistemáticos para construir la plataforma RAG Multimodal, utilizando `uv` y PowerShell.

## Fase 1: Configuración del Entorno
- [ ] Inicializar entorno Python con `uv`.
- [ ] Estructurar carpetas (`app/backend`, `docs`).
- [ ] Configurar `.gitignore` y `.dockerignore`.
- [ ] **Validación:** Verificar entorno virtual activo.

## Fase 2: Backend Core (FastAPI & GCS Opcional)
- [ ] Configurar FastAPI y dependencias (`uv add fastapi uvicorn google-cloud-storage chromadb google-generativeai`).
- [ ] Implementar endpoint de consulta RAG (`POST /chat`).
- [ ] Implementar servicios de subida/eliminación/listado de documentos.
- [ ] Implementar validación de bucket GCS (opcional).
- [ ] Implementar validación de tipos, tamaños y límites de carga.
- [ ] Implementar endpoint `/health` y `/metrics`.
- [ ] **Validación:** Tests de integración para endpoints de GCS y simulación de buckets inválidos.

## Fase 3: Lógica RAG Multimodal & Persistencia
- [ ] Adaptar `intro_multimodal_rag_utils.py` a la estructura del backend.
- [ ] **Configurar ChromaDB como almacén vectorial local.**
- [ ] Implementar sincronización ChromaDB <-> GCS (opcional, al inicio/final).
- [ ] **Pipeline de ingesta modular:**
  - [ ] Implementar extracción de contenido (PDF, Markdown, imágenes).
  - [ ] Implementar chunking configurable.
  - [ ] Implementar generación de descripciones (Gemini SDK).
  - [ ] Implementar generación de embeddings.
  - [ ] Implementar almacenamiento en ChromaDB.
- [ ] Implementar estados del documento (Uploaded, Processing, Indexed, Error).
- [ ] Implementar sincronización y reindexación manual.
- [ ] Implementar recuperación de fuentes (trazabilidad).
- [ ] **Validación:** Tests unitarios (mocking), verificación de persistencia local, verificación de trazabilidad.

## Fase 4: Frontend (Jinja2 Templates)
- [ ] Implementar UI con plantillas Jinja2 dentro de FastAPI.
- [ ] UI de configuración (Input bucket GCS, API Key).
- [ ] UI de Upload (drag & drop) integrado con API.
- [ ] Panel de gestión (listado, estado de indexación, borrar).
- [ ] Interfaz de chat (respuestas, citas, preguntas sugeridas).
- [ ] **Validación:** Pruebas manuales de flujo (carga, chat, sugerencias).

## Fase 5: Infraestructura, CI/CD y Despliegue
- [ ] Crear `Dockerfile` multi-stage.
- [ ] Crear workflow de GitHub Actions para build/push a GHCR.
- [ ] Configurar despliegue en Cloud Run.
- [ ] Gestionar secretos (env variables).
- [ ] Documentar despliegue en `README.md`.
- [ ] **Validación:** Verificación de logs en Cloud Run y ejecución desde imagen en entorno limpio.

## Fase 6: Validación y QA
- [ ] Tests unitarios (`pytest`) para pipeline de procesamiento.
- [ ] Medir tiempo de indexación y latencia de consulta.
- [ ] Verificar flujo completo de extremo a extremo.
- [ ] **Validación:** QA final de seguridad y rendimiento.

## Fase 7: Verificación de Rúbrica
- [ ] Verificar arranque con único comando `docker run`.
- [ ] Verificar README con pasos exigidos.
- [ ] Verificar inyección de API Keys vía variables de entorno.
- [ ] Ejecutar prueba completa siguiendo únicamente el README.
- [ ] **Validación:** Simulación de entorno limpio para evaluación del profesor.
