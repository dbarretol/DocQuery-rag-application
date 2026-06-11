# INITIAL-IDEA.md: Intelligent Multimodal RAG Platform

## 1. Descripción general de la aplicación
Una plataforma web para la consulta inteligente de documentos (PDF, Markdown, Imágenes). La aplicación permite a los usuarios cargar archivos, configurar el comportamiento del modelo de IA y realizar preguntas complejas sobre el contenido, obteniendo respuestas fundamentadas con citas directas a las fuentes utilizadas (texto o imágenes).

## 2. Objetivo y caso de uso
**Objetivo:** Permitir a los usuarios explorar grandes corpus de documentos mixtos (texto + tablas/imágenes) sin necesidad de leerlos completos, utilizando las capacidades multimodales de Gemini.
**Caso de uso:** Análisis rápido de informes financieros (como los archivos 10-K del repositorio legado) u otros documentos técnicos donde la información crítica reside tanto en párrafos de texto como en tablas, gráficos y diagramas.

## 3. Arquitectura de alto nivel
La aplicación seguirá una arquitectura cliente-servidor:
*   **Frontend:** Interfaz web sencilla (React o Angular + Vanilla CSS) para carga de archivos, configuración y chat.
*   **Backend:** API RESTful (FastAPI) para gestionar el procesamiento, la indexación y la comunicación con el modelo de IA.
*   **Almacenamiento:** Sistema de archivos local para documentos originales/imágenes y una base de datos vectorial simple o almacenamiento local estructurado (metadata JSON/Parquet) para los índices y embeddings.
*   **IA/ML:** Gemini API (Vertex AI) para generación de descripciones de imágenes, embeddings y respuestas a consultas.

## 4. Componentes principales
*   **Upload Manager:** Zona drag & drop para carga de documentos.
*   **Config Service:** Panel para gestionar las claves de API y seleccionar el modelo (por ej. `gemini-2.5-flash`).
*   **Indexing Engine:** Extrae texto/imágenes, genera embeddings y construye el índice semántico reutilizando la lógica de `intro_multimodal_rag_utils.py`.
*   **RAG Engine:** Realiza la búsqueda semántica, recupera el contexto (texto + imágenes pertinentes) y genera la respuesta con citas.

## 5. Flujo de usuario
1.  **Configuración:** El usuario ingresa la API Key y configura el modelo.
2.  **Carga:** Arrastra los documentos a la zona de carga.
3.  **Procesamiento:** El backend procesa los archivos, genera embeddings y los indexa.
4.  **Consulta:** El usuario escribe una pregunta en el chat.
5.  **Respuesta:** El sistema presenta la respuesta con fuentes citadas y sugiere preguntas relacionadas.

## 6. Tecnologías recomendadas
*   **Lenguaje:** Python (gestionado con `uv`).
*   **API Framework:** FastAPI.
*   **Frontend:** React (TypeScript).
*   **Embeddings & LLM:** Google Vertex AI / Gemini API.
*   **Procesamiento PDF:** PyMuPDF (`fitz`).
*   **Deployment:** Docker (multi-stage build).

## 7. Estrategia de procesamiento e indexación
*   Reutilizar la lógica de `intro_multimodal_rag_utils.py` para la extracción de texto, fragmentación (chunking), y extracción de imágenes.
*   Utilizar `TextEmbeddingModel` para texto y `MultiModalEmbeddingModel` para imágenes.
*   Almacenar metadatos en un formato persistente (parquets o JSON estructurado) para evitar reprocesamiento.

## 8. Estrategia de generación de respuestas y citación
*   **Retrieval:** Búsqueda por similitud de coseno sobre embeddings de usuario comparados con los embeddings almacenados.
*   **Augmentation:** Recuperar fragmentos de texto y descripciones de imágenes (previamente generadas por Gemini).
*   **Generation:** Enviar al modelo `user_query + context (textos + imágenes) + instrucciones de citación`.
*   **Citations:** El sistema devolverá un JSON estructurado indicando qué página, archivo y fragmento (o imagen) se usó, para que la UI renderice la fuente visiblemente.

## 9. Consideraciones de despliegue mediante Docker
*   Dockerfile multietapa:
    *   *Build:* Instalar dependencias mediante `uv`.
    *   *Runtime:* Imagen base ligera (Python slim), copiar solo el entorno virtual y el código fuente.
*   Ejecución: `docker run --rm -p 8000:8000 -e API_KEY=... TU_IMAGEN`
*   Variables de entorno para la configuración de la API.

## 10. Cumplimiento con la Rúbrica (@docs\RUBRIC-DETAILS.md)

| Criterio | Estrategia de Cumplimiento |
| :--- | :--- |
| **Arranca con 1 docker run** | Dockerfile optimizado; README con comandos claros. |
| **IA funcional y pertinente** | Uso de Gemini API con RAG multimodal probado en el lab. |
| **README claro** | Estructura detallada: requisitos, build, run, ejemplo. |
| **Puntos extra** | Estructura Git limpia, `uv` lock, `pytest`, `ruff`. |
