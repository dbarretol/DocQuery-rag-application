# TASKS.md: Roadmap de Implementación

Orden de prioridad: **los criterios de 12 pts base primero**, puntos extra al final.
Entorno: Python con `uv`, PowerShell en Windows.

---

## Fase 1: Configuración del entorno

- [ ] `uv init` y configurar `pyproject.toml`.
- [ ] Estructurar carpetas según ARCHITECTURE.md.
- [ ] Crear `.gitignore` (Python + uv + secrets) y `.dockerignore`.
- [ ] `uv add --dev ruff pytest`.
- [ ] Configurar `[tool.ruff]` en `pyproject.toml` (target Python 3.12, line-length 100).
- [ ] Inicializar repositorio Git y primer commit limpio (sin secretos).

**Validación:** `ruff check .` sin errores; `git status` no muestra archivos sensibles.

---

## Fase 2: Backend core

- [ ] `uv add fastapi uvicorn[standard] python-multipart jinja2`.
- [ ] `uv add chromadb google-generativeai pymupdf`.
- [ ] `uv add prometheus-fastapi-instrumentator`.
- [ ] `uv add google-cloud-storage` (para modo GCS opcional).
- [ ] Implementar `main.py`: app FastAPI con rutas stub, logging JSON, middleware CORS.
- [ ] Implementar `/health` → `{"status": "ok"}`.
- [ ] Implementar `/metrics` con `prometheus-fastapi-instrumentator`.
- [ ] Implementar endpoint `POST /upload` (stub: recibe archivo, valida tipo/tamaño, devuelve 202).
- [ ] Implementar endpoint `GET /documents` (stub: devuelve lista vacía).
- [ ] Implementar endpoint `DELETE /documents/{doc_id}` (stub).
- [ ] Implementar endpoint `POST /chat` (stub: recibe `{"question": "..."}`, devuelve `{"answer": "stub"}`).
- [ ] Servir UI básica con Jinja2 (página principal con formulario de chat y upload).

**Validación:** `uv run uvicorn app.backend.main:app --reload` arranca sin errores; `/health` responde 200; `/metrics` responde 200.

---

## Fase 3: Lógica RAG

> Esta es la fase crítica. Completar antes de tocar Docker o CI/CD.

- [ ] **`storage/chroma.py`:** cliente ChromaDB apuntando a `/data/chroma` (configurable vía env `CHROMA_PATH`, default `./data/chroma` para desarrollo local).
- [ ] **`rag/ingest.py`:** pipeline completo:
  - [ ] Extracción PDF con PyMuPDF (texto por página + imágenes a base64).
  - [ ] Extracción Markdown (texto plano).
  - [ ] Descripción de imágenes vía Gemini (`gemini-1.5-flash`).
  - [ ] Chunking por párrafos (tamaño configurable, default 500 tokens).
  - [ ] Embeddings con `text-embedding-004` de Gemini SDK.
  - [ ] Almacenamiento en ChromaDB con metadatos: `{filename, page, chunk_index, content_type}`.
  - [ ] Manejo de estados: `UPLOADED → PROCESSING → INDEXED / ERROR`.
- [ ] **`rag/retrieval.py`:** búsqueda semántica top-k en ChromaDB (default k=5).
- [ ] **`rag/generation.py`:** construcción de prompt con contexto + llamada a `gemini-1.5-flash` + extracción de fuentes citadas.
- [ ] **Integrar pipeline en `POST /upload`:** procesamiento asíncrono (background task de FastAPI).
- [ ] **Integrar RAG en `POST /chat`:** retrieval + generation reales; respuesta incluye `{"answer": "...", "sources": [...]}`.
- [ ] **`storage/gcs.py`:** sincronización opcional (descarga índice al arranque si `GCS_BUCKET` definido; sube tras indexar). No bloqueante: errores se loguean, no crashean el servidor.

**Validación:** subir un PDF real, hacer una pregunta sobre su contenido, verificar que la respuesta es pertinente y cita fuentes.

---

## Fase 4: UI (Jinja2)

- [ ] Página principal: formulario de chat + área de respuesta con fuentes.
- [ ] Panel de upload: drag & drop o file input, barra de progreso/estado.
- [ ] Panel de documentos: tabla con nombre, estado (INDEXED/ERROR), botón de borrar.
- [ ] UI de configuración: input de `GCS_BUCKET` (solo este campo; API key nunca en UI).
- [ ] Preguntas sugeridas: botones de ejemplo que auto-completan el chat.

**Validación:** flujo completo manual: subir → esperar INDEXED → preguntar → ver respuesta con citas.

---

## Fase 5: Docker

> Sin Docker local: el Dockerfile se escribe aquí pero el build se ejecuta en GitHub Actions / Cloud Build.

- [ ] Crear `Dockerfile` multi-stage:
  ```
  Stage 1 (builder): python:3.12-slim + uv, instala dependencias con lockfile
  Stage 2 (runtime): python:3.12-slim, copia solo el entorno virtual y el código
  ```
- [ ] Verificar que `GEMINI_API_KEY` se lee de env, no está hardcodeada.
- [ ] Verificar que `CHROMA_PATH` apunta a `/data/chroma` en el contenedor.
- [ ] Agregar `VOLUME ["/data/chroma"]` en el Dockerfile.
- [ ] Crear `cloudbuild.yaml` como alternativa de build en GCP (backup si GitHub Actions falla).

**Validación:** el Dockerfile pasa `docker build` en GitHub Actions sin errores (ver Fase 6).

---

## Fase 6: CI/CD y publicación

- [ ] Crear `.github/workflows/ci.yml`:
  - [ ] Trigger: `push` a `main`.
  - [ ] Job lint: `ruff check .`.
  - [ ] Job test: `pytest tests/`.
  - [ ] Job build+push (solo si lint y test pasan):
    - `docker build`
    - `docker push ghcr.io/${{ github.repository }}:latest`
    - `docker push ghcr.io/${{ github.repository }}:${{ github.sha }}`
- [ ] Configurar secret `GHCR_TOKEN` en GitHub (Personal Access Token con `write:packages`).
- [ ] Verificar que la imagen en GHCR es **pública** (el profesor no tiene credenciales).
- [ ] Hacer push a `main` y confirmar que el workflow completa sin errores.
- [ ] Confirmar que `docker pull ghcr.io/USER/REPO:latest` funciona sin login.

**Validación:** el profesor puede hacer `docker pull` y `docker run` siguiendo solo el README.

---

## Fase 7: Tests y lint

- [ ] `tests/test_ingest.py`: tests unitarios del pipeline con mocks de Gemini y ChromaDB.
- [ ] `tests/test_chat.py`: test del endpoint `/chat` con respuesta mockeada.
- [ ] `tests/test_health.py`: test trivial de `/health`.
- [ ] Ejecutar `ruff check .` y corregir todos los warnings.
- [ ] Ejecutar `pytest` y verificar que todos los tests pasan.

**Validación:** `pytest` verde en local (con `uv run pytest`) y en CI.

---

## Fase 8: README y verificación final

> Esta fase es la más importante para la nota. El README son 3 pts directos.

- [ ] Redactar `README.md` con estas secciones exactas:
  1. **Descripción** (2-3 líneas).
  2. **Requisitos** (solo: Docker, una Gemini API key).
  3. **Cómo correr:**
     ```bash
     docker pull ghcr.io/USER/REPO:latest
     docker run --rm -p 8000:8000 \
       -e GEMINI_API_KEY=tu_clave \
       -v chroma_data:/data/chroma \
       ghcr.io/USER/REPO:latest
     ```
  4. **Ejemplo de uso** (entrada y salida real, copiada del sistema funcionando).
  5. **Cómo construir la imagen** (para quien quiera hacer el build local).
  6. **Variables de entorno** (tabla: `GEMINI_API_KEY` obligatoria, `GCS_BUCKET` opcional).
- [ ] Ejecutar el README de principio a fin en un entorno limpio (sin contexto previo).
- [ ] Verificar que el ejemplo del README produce exactamente la salida documentada.
- [ ] Verificar que no hay secretos en el repo (`git log --all` + búsqueda manual).

**Validación final:** el profesor sigue el README sin ayuda y la app responde correctamente a su pregunta.