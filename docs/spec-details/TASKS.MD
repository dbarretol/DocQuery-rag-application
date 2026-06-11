# TASKS.MD: Roadmap de Implementación

Este documento define los paquetes de trabajo sistemáticos para construir la plataforma RAG Multimodal, utilizando `uv` y PowerShell.

## Fase 1: Configuración del Entorno y Proyecto
- [ ] Inicializar entorno Python con `uv`.
- [ ] Estructurar carpetas (`app/backend`, `app/frontend`, `docs`).
- [ ] Configurar `.gitignore` y `.dockerignore`.
- [ ] Configurar pre-commit hooks (ruff, etc.).
- [ ] **Validación:** Verificar entorno virtual activo y linting básico.

## Fase 2: Backend Core (FastAPI & GCS)
- [ ] Configurar FastAPI y dependencias base (`uv add fastapi uvicorn google-cloud-storage`).
- [ ] Implementar endpoint de validación de bucket GCS.
- [ ] Implementar servicios de subida/eliminación/listado de documentos en GCS.
- [ ] Crear endpoints de gestión documental (listar, borrar).
- [ ] Implementar manejo de errores de bucket (inexistente, privado, permisos, conectividad).
- [ ] Implementar validación de tipos, tamaños y límites de carga de archivos.
- [ ] **Validación:** Tests de integración para endpoints de GCS y simulación de buckets inválidos.

## Fase 3: Lógica RAG Multimodal (Reutilización de `legacy/`)
- [ ] Adaptar `intro_multimodal_rag_utils.py` a la estructura del backend.
- [ ] Definir y configurar el almacén vectorial (ChromaDB/FAISS/Vertex AI Vector Search).
- [ ] Implementar persistencia del índice para evitar reindexación al reiniciar.
- [ ] Implementar servicio de indexación: extracción -> descripción (Gemini) -> embeddings -> almacenamiento.
- [ ] Implementar sincronización entre documentos en GCS y registros del índice.
- [ ] Asociar metadatos a cada chunk (archivo, página, sección, posición).
- [ ] Implementar motor de búsqueda semántica (Retrieval) recuperando fuentes utilizadas.
- [ ] Implementar servicio de generación de respuesta con referencias estructuradas.
- [ ] Implementar eliminación completa: GCS + registros de embeddings/índice + limpieza de chunks huérfanos.
- [ ] **Validación:** Tests unitarios (mocking Gemini/GCS), validación de persistencia tras reinicio, verificación de eliminación completa y trazabilidad de fuentes.

## Fase 4: Frontend (Next.js)
- [ ] Inicializar proyecto Next.js en `app/frontend`.
- [ ] Implementar UI de configuración (Input de nombre de bucket GCS).
- [ ] Implementar componente Upload (drag & drop) integrado con API backend.
- [ ] Implementar panel de gestión documental (listado + acciones de borrar).
- [ ] Implementar interfaz de chat con soporte para mostrar citas y fuentes.
- [ ] Implementar generación automática de preguntas sugeridas y funcionalidad de clic para enviar.
- [ ] **Validación:** Tests e2e (Cypress/Playwright) de flujo de carga, chat y preguntas sugeridas.

## Fase 5: Infraestructura, CI/CD y Despliegue
- [ ] Crear `Dockerfile` multi-stage (optimizado para tamaño y seguridad).
- [ ] Crear `cloudbuild.yaml` para automatizar build y push a Artifact Registry.
- [ ] Configurar servicios en GCP (Artifact Registry, Cloud Run).
- [ ] Gestionar secretos mediante variables de entorno.
- [ ] Implementar endpoint `/health` y `/metrics`.
- [ ] Configurar logging estructurado para Cloud Run.
- [ ] Definir IAM mínima (`roles/storage.objectViewer`).
- [ ] Documentar despliegue en `README.md`.
- [ ] **Validación:** Test de despliegue en Cloud Run, verificación de logs/métricas y seguridad de secretos.

## Fase 6: Validación y QA
- [ ] Escribir tests unitarios adicionales (`pytest`) para cobertura total.
- [ ] Ejecutar linting (`ruff`) y formateo.
- [ ] Verificar el flujo completo: Carga -> Indexación -> Consulta RAG -> Citas.
- [ ] **Validación:** QA final de rendimiento y seguridad.

## Fase 7: Verificación de Rúbrica
- [ ] Verificar arranque con único comando `docker run`.
- [ ] Verificar README con pasos exigidos.
- [ ] Verificar inyección de API Keys vía variables de entorno.
- [ ] Verificar ejecución sin dependencias locales adicionales.
- [ ] Ejecutar prueba completa siguiendo únicamente el README (simulación de evaluación).
- [ ] **Validación:** Simulación de entorno limpio para evaluación del profesor.
