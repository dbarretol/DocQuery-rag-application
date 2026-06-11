# ARCHITECTURE.md: Intelligent Multimodal RAG Platform

## 1. Diagrama de alto nivel

```
Usuario
  │
  ▼
FastAPI + Jinja2 (puerto 8000)
  │
  ├── /upload      → Pipeline de ingesta
  ├── /chat        → Pipeline RAG
  ├── /documents   → Gestión documental
  ├── /health      → Health check
  └── /metrics     → Prometheus metrics
  │
  ├── ChromaDB ────────────────── volumen Docker /data/chroma
  ├── Gemini API (google-genai) ── red, requiere GEMINI_API_KEY
  └── GCS Client ──────────────── opcional, requiere GCS_BUCKET
```

## 2. Flujo de ingestión

```
Usuario sube archivo (PDF / MD / imagen)
  │
  ▼
Validación (tipo, tamaño)
  │
  ▼
Extracción de contenido
  ├── PDF     → PyMuPDF (texto por página + imágenes)
  ├── MD      → texto plano
  └── Imagen  → descripción generada por Gemini
  │
  ▼
Chunking configurable
  │
  ▼
Generación de embeddings (Gemini text-embedding-004  este valor es configurable)
  │
  ▼
Almacenamiento en ChromaDB
  │  (metadatos: archivo, página, chunk_index, tipo)
  │
  └── [Opcional] Sincronización a GCS
```

## 3. Flujo de consulta RAG

```
Pregunta del usuario
  │
  ▼
Generación de embedding de la query (Gemini)
  │
  ▼
Búsqueda por similitud coseno en ChromaDB (top-k chunks)
  │
  ▼
Construcción del prompt con contexto recuperado
  │
  ▼
Generación con Gemini Flash (gemini-1.5-flash este valor es configurable en pantalla)
  │
  ▼
Respuesta + lista de fuentes citadas (archivo, página)
```

## 4. Componentes técnicos

### Backend (FastAPI)
- Gestión de paquetes: `uv` con lockfile (`uv.lock`).
- Métricas: `prometheus-fastapi-instrumentator` expone `/metrics`.
- Logging: estructurado (JSON) para compatibilidad con Cloud Run.
- GCS: validación no bloqueante al arranque. Si `GCS_BUCKET` no está definido o falla, el sistema opera en modo local sin degradación.

### Persistencia
- ChromaDB en modo persistente apuntando a `/data/chroma` dentro del contenedor.
- El usuario monta el volumen con `-v chroma_data:/data/chroma` para preservar el índice entre sesiones.
- Sin volumen: el índice se pierde al detener el contenedor (comportamiento válido para evaluación).

### Estados de documento
```
UPLOADED → PROCESSING → INDEXED
                      → ERROR
```

## 5. CI/CD

```
git push
  │
  ▼
GitHub Actions
  ├── ruff check .          (lint)
  ├── pytest                (tests unitarios)
  └── docker build + push
        ├── ghcr.io/USER/REPO:latest
        └── ghcr.io/USER/REPO:${{ github.sha }}
```

La imagen en GHCR es pública. El profesor hace `docker pull` sin autenticación.

## 6. Despliegue en Cloud Run

```bash
gcloud run deploy rag-platform \
  --image ghcr.io/USER/REPO:latest \
  --set-env-vars GEMINI_API_KEY=... \
  --port 8000
```

IAM requerida solo si se activa GCS: `roles/storage.admin` en la cuenta de servicio de Cloud Run.

## 7. Estructura de carpetas

```
/
├── app/
│   └── backend/
│       ├── main.py              # FastAPI app, rutas
│       ├── rag/
│       │   ├── ingest.py        # Pipeline de ingesta
│       │   ├── retrieval.py     # Búsqueda semántica
│       │   └── generation.py    # Llamada a Gemini
│       ├── storage/
│       │   ├── chroma.py        # Cliente ChromaDB
│       │   └── gcs.py           # Cliente GCS (opcional)
│       └── templates/           # Jinja2 HTML
├── tests/
├── Dockerfile
├── .github/workflows/ci.yml
├── pyproject.toml               # uv + ruff config
├── uv.lock
├── .gitignore
├── .dockerignore
└── README.md
```