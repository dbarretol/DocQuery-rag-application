# Arquitectura del Sistema: Intelligent Multimodal RAG Platform (MVP Evaluable)

Este documento detalla la arquitectura técnica simplificada para garantizar la evaluabilidad del proyecto.

## 1. Diagrama de Arquitectura de Alto Nivel

```mermaid
graph TD
    User((Usuario)) --> UI[FastAPI + Jinja2 UI]
    UI --> API[FastAPI Backend]
    
    subgraph "Containerized RAG Core"
        API --> ChromaDB[(ChromaDB Local)]
        API --> GCS[GCS Client (Opcional)]
    end
    
    subgraph "External AI"
        API --> Gemini[Gemini API]
    end
    
    subgraph "CI/CD & Deployment"
        GH[GitHub] --> GHA[GitHub Actions]
        GHA --> GHCR[GitHub Container Registry]
        GHCR --> CR[Cloud Run]
    end
```

## 2. Flujo de Datos

### 2.1. Ingestión y Procesamiento
1.  **Carga:** El usuario sube archivos a través del formulario simple (UI).
2.  **Procesamiento:** 
    *   Extracción, Chunking, Generación de descripciones, Embeddings.
    *   Almacenamiento en **ChromaDB Local**.
3.  **Persistencia:** Si `GCS_BUCKET` está configurado, se sincroniza el índice de ChromaDB con el bucket GCS.

### 2.2. Consulta RAG (Multimodal)
1.  **Retrieval:** Búsqueda semántica en ChromaDB.
2.  **Augmentation:** Recuperación de contexto.
3.  **Generation:** Consulta vía `google-generativeai` SDK.

## 3. Componentes Técnicos

*   **Frontend:** Integrado en FastAPI mediante plantillas Jinja2 (sin JS externo complejo).
*   **Backend:** FastAPI con gestión de paquetes `uv`.
*   **Persistencia:** ChromaDB local (persistido en volumen Docker).

## 4. Infraestructura y Despliegue (GCP/Local)

*   **GitHub Actions:** Automatiza el build/push a GitHub Container Registry (GHCR).
*   **Cloud Run:** Despliegue del contenedor.
*   **Gestión IAM:** Se requiere si se configura sincronización con GCS (`roles/storage.admin`).

## 5. Gestión de Documentos
La eliminación implica:
1.  `DELETE /documents/{doc_id}`.
2.  Borrado en ChromaDB + GCS (si aplica).
3.  Reindexación y respuesta síncrona.
