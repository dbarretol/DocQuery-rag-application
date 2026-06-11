# INITIAL-IDEA.md: Intelligent Multimodal RAG Platform (GCP Edition)

## 1. Descripción general
Plataforma web para consulta inteligente de documentos almacenados en Google Cloud Storage (GCS). Permite indexar, consultar y gestionar documentos mixtos (PDF, MD, Imágenes) utilizando capacidades multimodales de Gemini en GCP.

## 2. Objetivo y caso de uso
**Objetivo:** Explorar corpus documentales en GCS mediante RAG multimodal, garantizando trazabilidad y manejo de contexto visual.  
**Caso de uso:** Análisis corporativo de informes financieros y técnicos alojados en GCS, con indexación centralizada y persistente.

## 3. Arquitectura de alto nivel
*   **Frontend:** Next.js (TypeScript) para la interfaz de usuario.
*   **Backend:** FastAPI en Python (gestión `uv`).
*   **Almacenamiento de Documentos:** Google Cloud Storage (GCS).
*   **IA/ML:** Gemini API (Vertex AI).
*   **Despliegue:** Cloud Run (contenedor Docker), CI/CD vía Cloud Build y Artifact Registry.

## 4. Componentes y Flujo
*   **Gestión GCS:** Interfaz para definir bucket público. Validación de acceso al iniciar.
*   **Ingestión:** El usuario sube archivos -> Se guardan en GCS -> Se disparan funciones de procesamiento -> Indexación en memoria/persistente.
*   **Gestión Documental:** Interfaz para listar, ver y eliminar archivos indexados (sincronizando GCS y el índice).

## 5. Tecnologías
*   **Backend:** Python (`uv`), FastAPI, Google Cloud Storage Client.
*   **Frontend:** Next.js (TypeScript).
*   **IA:** Vertex AI (Gemini Flash), Multimodal Embeddings.
*   **Despliegue:** Docker, Cloud Build, Artifact Registry, Cloud Run.

## 6. Infraestructura y despliegue en Google Cloud
### Componentes GCP
*   **Cloud Storage:** Almacenamiento centralizado de documentos para ingestión.
*   **Artifact Registry:** Almacén de imágenes Docker.
*   **Cloud Build:** Automatización de CI/CD (build y push).
*   **Cloud Run:** Plataforma de ejecución escalable del servicio.

### Flujos
*   **Ingestión:** `UI (Config Bucket)` -> `Backend (Validación GCP/GCS)` -> `Upload GCS` -> `Procesamiento/Embeddings` -> `Actualización de Índice`.
*   **Consultas RAG:** `User Query` -> `Retrieval (GCS context)` -> `Augmentation` -> `Gemini Generation` -> `Citas`.
*   **Gestión Documentos:** El backend expone endpoints para listar/eliminar en GCS y actualizar el índice local (JSON/Parquet).

### CI/CD
1.  `Push` a GitHub -> Cloud Build detecta cambios.
2.  Cloud Build compila la imagen Docker.
3.  Imagen enviada a Artifact Registry.
4.  Cloud Run despliega automáticamente la nueva versión.

### Variables y Permisos
*   **Variables:** `BUCKET_NAME`, `PROJECT_ID`, `GCP_REGION`, `API_KEY` (secret manager).
*   **IAM:** La cuenta de servicio de Cloud Run requiere `roles/storage.objectViewer` (o Admin según alcance).

## 7. Cumplimiento con la Rúbrica
| Criterio | Estrategia de Cumplimiento |
| :--- | :--- |
| **Arranca con 1 docker run** | Imagen en Cloud Run/Docker; README con comandos. |
| **IA funcional** | RAG multimodal con Gemini en Vertex AI. |
| **README claro** | Guía de configuración GCP, despliegue y uso. |
| **Puntos extra** | Dockerfile multi-stage, `uv`, CI/CD (Cloud Build). |
