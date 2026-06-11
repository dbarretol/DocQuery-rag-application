# INITIAL-IDEA.md: Intelligent Multimodal RAG Platform (MVP Evaluable)

## 1. Descripción general
Plataforma web para consulta inteligente de documentos. Permite indexar, consultar y gestionar documentos mixtos (PDF, MD, Imágenes) utilizando capacidades multimodales de Gemini. Arquitectura optimizada para ser evaluable mediante un solo `docker run` sin dependencias externas obligatorias.

## 2. Objetivo y caso de uso
**Objetivo:** Explorar corpus documentales mediante RAG multimodal, garantizando trazabilidad y contexto visual.
**Caso de uso:** Análisis rápido de informes (ej. 10-K) con indexación persistente local (ChromaDB) y sincronización opcional con GCS.

## 3. Arquitectura de alto nivel
*   **Frontend/Backend:** Integrados en un solo servicio FastAPI usando plantillas Jinja2 (sin Node.js).
*   **Almacenamiento:** ChromaDB local (persistido en volumen Docker). Sincronización opcional con GCS.
*   **IA/ML:** Gemini API (SDK `google-generativeai`).
*   **Despliegue:** Cloud Run (contenedor Docker), CI/CD vía GitHub Actions y GHCR.

## 4. Componentes y Flujo
*   **Gestión GCS (Opcional):** Configuración de bucket GCS. Validación al iniciar (No bloqueante). Si falla, opera en modo local puro.
*   **Ingestión:** Subida de archivos -> Procesamiento (Chunking, Embeddings mediante Gemini SDK) -> Almacenamiento en ChromaDB.
*   **Gestión Documental:** Interfaz para listar, ver y eliminar archivos indexados.

## 5. Tecnologías
*   **Backend:** Python (`uv`), FastAPI, Jinja2, `google-generativeai`, `chromadb`.
*   **Despliegue:** Docker, GitHub Actions, GHCR, Cloud Run.

## 6. Infraestructura y despliegue
### Flujos
*   **Ingestión:** `UI` -> `FastAPI Backend` -> `Procesamiento/Embeddings (SDK google-generativeai)` -> `ChromaDB` -> `Sincronización GCS (Opcional)`.
*   **Consultas RAG:** `User Query` -> `Retrieval (ChromaDB)` -> `Gemini Generation` -> `Respuesta + Citas`.

### CI/CD
1. `Push` a GitHub -> GitHub Actions compila Docker.
2. Imagen enviada a GHCR (GitHub Container Registry).
3. Despliegue en Cloud Run (o ejecución local).

### Variables y Permisos
*   **Variables:** `API_KEY` (Gemini), `GCS_BUCKET` (opcional). 
    *   *Nota: La API Key se inyecta exclusivamente vía variable de entorno en el contenedor, nunca a través de la UI.*
*   **IAM:** Si se usa GCS, cuenta de servicio con `roles/storage.admin`.

## 7. Cumplimiento con la Rúbrica
| Criterio | Estrategia de Cumplimiento |
| :--- | :--- |
| **Arranca con 1 docker run** | Imagen autocontenida; modo local offline por defecto. |
| **IA funcional** | RAG multimodal con SDK `google-generativeai`. |
| **README claro** | Guía de ejecución simple; ejemplo de entrada/salida. |
| **Puntos extra** | Dockerfile multi-stage, `uv`, GitHub Actions, logs/métricas. |
