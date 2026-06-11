# TASKS.MD: Roadmap de Implementación

Este documento define los paquetes de trabajo sistemáticos para construir la plataforma RAG Multimodal, utilizando `uv` y PowerShell.

## Fase 1: Configuración del Entorno y Proyecto
- [ ] Inicializar entorno Python con `uv`.
- [ ] Estructurar carpetas (`app/backend`, `app/frontend`, `docs`).
- [ ] Configurar `.gitignore` y `.dockerignore`.
- [ ] Configurar pre-commit hooks (ruff, etc.).

## Fase 2: Backend Core (FastAPI & GCS)
- [ ] Configurar FastAPI y dependencias base (`uv add fastapi uvicorn google-cloud-storage`).
- [ ] Implementar endpoint de validación de bucket GCS.
- [ ] Implementar servicios de subida/eliminación/listado de documentos en GCS.
- [ ] Crear endpoints de gestión documental (listar, borrar).

## Fase 3: Lógica RAG Multimodal (Reutilización de `legacy/`)
- [ ] Adaptar `intro_multimodal_rag_utils.py` a la estructura del backend.
- [ ] Implementar servicio de indexación: extracción -> descripción (Gemini) -> embeddings -> almacenamiento.
- [ ] Implementar motor de búsqueda semántica (Retrieval).
- [ ] Implementar servicio de generación de respuesta (Augmentation + Generation).

## Fase 4: Frontend (Next.js)
- [ ] Inicializar proyecto Next.js en `app/frontend`.
- [ ] Implementar UI de configuración (Input de nombre de bucket GCS).
- [ ] Implementar componente Upload (drag & drop) integrado con API backend.
- [ ] Implementar panel de gestión documental (listado + acciones de borrar).
- [ ] Implementar interfaz de chat con soporte para mostrar citas y fuentes.

## Fase 5: Infraestructura, CI/CD y Despliegue
- [ ] Crear `Dockerfile` multi-stage (optimizado para tamaño y seguridad).
- [ ] Crear `cloudbuild.yaml` para automatizar build y push a Artifact Registry.
- [ ] Configurar servicios en GCP (Artifact Registry, Cloud Run).
- [ ] Definir IAM mínima necesaria para la cuenta de servicio de Cloud Run (`roles/storage.objectViewer`).
- [ ] Documentar despliegue en `README.md`.

## Fase 6: Validación y QA
- [ ] Escribir tests unitarios (`pytest`) para el core de procesamiento.
- [ ] Ejecutar linting (`ruff`).
- [ ] Verificar el flujo completo: Carga -> Indexación -> Consulta RAG -> Citas visuales.
