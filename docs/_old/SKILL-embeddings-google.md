---
name: gemini-embeddings
description: >
  Guía para generar embeddings con la API de Gemini usando texto e imágenes
  (PNG, JPEG) mediante Python o REST. Úsala siempre que el usuario quiera
  generar embeddings semánticos, hacer búsqueda vectorial, RAG, clasificación,
  clustering, similitud semántica, o comparar texto con imágenes usando
  gemini-embedding-2 o gemini-embedding-001. También aplica cuando pregunten
  sobre task types, dimensiones de salida, normalización, o almacenamiento en
  bases de datos vectoriales. No cubre audio ni video.
---

# Gemini Embeddings — Texto e Imagen
source: https://ai.google.dev/gemini-api/docs/embeddings
## Modelos disponibles

| Modelo | Entrada | Tokens entrada | Dimensiones salida |
|---|---|---|---|
| `gemini-embedding-2` | Texto, imagen (PNG/JPEG), PDF | 8 192 | 128–3072 (recomendado: 768, 1536, 3072) |
| `gemini-embedding-001` | Solo texto | 2 048 | 128–3072 (recomendado: 768, 1536, 3072) |

> **Importante:** Los espacios de embeddings de ambos modelos son **incompatibles**. Si migras de `gemini-embedding-001` a `gemini-embedding-2` debes re-embeber todos tus datos.

---

## 1. Embedding de texto

### Python

```python
from google import genai

client = genai.Client()

result = client.models.embed_content(
    model="gemini-embedding-2",
    contents="¿Cuál es el sentido de la vida?"
)

print(result.embeddings)
```

### REST

```bash
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-2:embedContent" \
  -H "Content-Type: application/json" \
  -H "x-goog-api-key: ${GEMINI_API_KEY}" \
  -d '{
    "model": "models/gemini-embedding-2",
    "content": {
      "parts": [{ "text": "¿Cuál es el sentido de la vida?" }]
    }
  }'
```

---

## 2. Task types — cómo formatear el prompt

### Con `gemini-embedding-2` (instrucción en el prompt)

**Casos asimétricos (query ≠ documento):**

```python
# Búsqueda semántica
def prepare_query(query):
    return f"task: search result | query: {query}"

def prepare_document(content, title=None):
    title = title or "none"
    return f"title: {title} | text: {content}"

# Question answering
# return f"task: question answering | query: {query}"

# Fact checking
# return f"task: fact checking | query: {query}"

# Recuperación de código
# return f"task: code retrieval | query: {query}"
```

**Casos simétricos (query = documento):**

```python
def prepare_symmetric(content):
    return f"task: classification | query: {content}"
    # return f"task: clustering | query: {content}"
    # return f"task: sentence similarity | query: {content}"
```

> **Regla clave:** el task prefix debe ser **consistente** entre query y documento.

### Con `gemini-embedding-001` (parámetro `task_type`)

```python
from google import genai
from google.genai import types

client = genai.Client()

result = client.models.embed_content(
    model="gemini-embedding-001",
    contents=["Texto A", "Texto B", "Texto C"],
    config=types.EmbedContentConfig(task_type="SEMANTIC_SIMILARITY")
)
```

**Task types soportados para `gemini-embedding-001`:**

| Task type | Uso |
|---|---|
| `SEMANTIC_SIMILARITY` | Similitud entre textos |
| `CLASSIFICATION` | Clasificar textos con etiquetas predefinidas |
| `CLUSTERING` | Agrupar textos por similaridad |
| `RETRIEVAL_DOCUMENT` | Indexar documentos para búsqueda |
| `RETRIEVAL_QUERY` | Consultas de búsqueda general |
| `CODE_RETRIEVAL_QUERY` | Recuperar bloques de código |
| `QUESTION_ANSWERING` | Preguntas en sistemas QA |
| `FACT_VERIFICATION` | Verificación de hechos |

---

## 3. Controlar el tamaño del embedding (output_dimensionality)

### Python

```python
from google import genai
from google.genai import types

client = genai.Client()

result = client.models.embed_content(
    model="gemini-embedding-2",
    contents="Texto de ejemplo",
    config=types.EmbedContentConfig(output_dimensionality=768)
)

embedding = result.embeddings[0]
print(f"Dimensiones: {len(embedding.values)}")
```

### REST

```bash
curl -X POST "https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-2:embedContent" \
  -H "Content-Type: application/json" \
  -H "x-goog-api-key: ${GEMINI_API_KEY}" \
  -d '{
    "content": { "parts": [{ "text": "Texto de ejemplo" }] },
    "output_dimensionality": 768
  }'
```

> `gemini-embedding-2` **auto-normaliza** dimensiones truncadas. Con `gemini-embedding-001` debes normalizar manualmente:

```python
import numpy as np

# Solo para gemini-embedding-001
values = np.array(embedding_obj.values)
normed = values / np.linalg.norm(values)
```

---

## 4. Embedding de imágenes

Solo `gemini-embedding-2`. Formatos: **PNG, JPEG**. Máximo **6 imágenes** por request.

### Python — imagen única

```python
from google import genai
from google.genai import types

client = genai.Client()

with open("imagen.png", "rb") as f:
    image_bytes = f.read()

result = client.models.embed_content(
    model="gemini-embedding-2",
    contents=[
        types.Part.from_bytes(data=image_bytes, mime_type="image/png")
    ]
)

print(result.embeddings)
```

### REST — imagen única (base64)

```bash
IMG_BASE64=$(base64 -w0 "/ruta/imagen.png")

curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-2:embedContent" \
  -H "Content-Type: application/json" \
  -H "x-goog-api-key: ${GEMINI_API_KEY}" \
  -d '{
    "content": {
      "parts": [{
        "inline_data": {
          "mime_type": "image/png",
          "data": "'"${IMG_BASE64}"'"
        }
      }]
    }
  }'
```

---

## 5. Embedding multimodal texto + imagen (agregado)

Combina texto e imagen en **un solo embedding** pasando múltiples partes en `contents`:

### Python

```python
from google import genai
from google.genai import types

client = genai.Client()

with open("perro.png", "rb") as f:
    image_bytes = f.read()

result = client.models.embed_content(
    model="gemini-embedding-2",
    contents=[
        "Una imagen de un perro",
        types.Part.from_bytes(data=image_bytes, mime_type="image/png"),
    ]
)

# Produce UN solo embedding agregado
print(result.embeddings[0].values)
```

### REST

```bash
IMG_BASE64=$(base64 -w0 "/ruta/perro.png")

curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-2:embedContent" \
  -H "Content-Type: application/json" \
  -H "x-goog-api-key: ${GEMINI_API_KEY}" \
  -d '{
    "content": {
      "parts": [
        { "text": "Una imagen de un perro" },
        { "inline_data": { "mime_type": "image/png", "data": "'"${IMG_BASE64}"'" } }
      ]
    }
  }'
```

---

## 6. Embeddings separados para texto e imagen (batch)

Si necesitas **embeddings individuales** por cada input, usa `Content` objects:

### Python

```python
from google import genai
from google.genai import types

client = genai.Client()

with open("perro.png", "rb") as f:
    image_bytes = f.read()

result = client.models.embed_content(
    model="gemini-embedding-2",
    contents=[
        types.Content(parts=[types.Part.from_text(text="Una imagen de un perro")]),
        types.Content(parts=[
            types.Part.from_bytes(data=image_bytes, mime_type="image/png")
        ]),
    ]
)

# Produce DOS embeddings separados
for emb in result.embeddings:
    print(emb.values)
```

### REST — batchEmbedContents

```bash
IMG_BASE64=$(base64 -w0 "/ruta/perro.png")

curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-2:batchEmbedContents" \
  -H "Content-Type: application/json" \
  -H "x-goog-api-key: ${GEMINI_API_KEY}" \
  -d '{
    "requests": [
      {
        "model": "models/gemini-embedding-2",
        "content": { "parts": [{ "text": "Una imagen de un perro" }] }
      },
      {
        "model": "models/gemini-embedding-2",
        "content": { "parts": [{ "inline_data": { "mime_type": "image/png", "data": "'"${IMG_BASE64}"'" } }] }
      }
    ]
  }'
```

---

## 7. Similitud coseno entre textos (ejemplo completo)

```python
from google import genai
from google.genai import types
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

client = genai.Client()

textos = [
    "¿Cuál es el sentido de la vida?",
    "¿Cuál es el propósito de la existencia?",
    "¿Cómo preparo un pastel?",
]

result = client.models.embed_content(
    model="gemini-embedding-001",
    contents=textos,
    config=types.EmbedContentConfig(task_type="SEMANTIC_SIMILARITY")
)

df = pd.DataFrame(
    cosine_similarity([e.values for e in result.embeddings]),
    index=textos,
    columns=textos,
)

print(df)
```

> Cosine similarity: valores de -1 (opuestos) a 1 (máxima similitud).

---

## 8. Embedding de PDFs

Solo `gemini-embedding-2`. Máximo **1 PDF** y **6 páginas** por request. Consume **258 tokens por página** (visual) + tokens de texto.

### Python

```python
from google import genai
from google.genai import types

client = genai.Client()

with open("documento.pdf", "rb") as f:
    pdf_bytes = f.read()

result = client.models.embed_content(
    model="gemini-embedding-2",
    contents=[
        types.Part.from_bytes(data=pdf_bytes, mime_type="application/pdf")
    ]
)

print(result.embeddings)
```

### REST

```bash
PDF_BASE64=$(base64 -w0 "/ruta/documento.pdf")

curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-2:embedContent" \
  -H "Content-Type: application/json" \
  -H "x-goog-api-key: ${GEMINI_API_KEY}" \
  -d '{
    "content": {
      "parts": [{
        "inline_data": {
          "mime_type": "application/pdf",
          "data": "'"${PDF_BASE64}"'"
        }
      }]
    }
  }'
```

---

## 9. Almacenamiento en bases de datos vectoriales

Para producción, usa una base de datos vectorial para indexar y recuperar embeddings:

| Opción | Tipo |
|---|---|
| Vertex AI Vector Search 2.0 | Google Cloud (managed) |
| BigQuery / AlloyDB / Cloud SQL | Google Cloud |
| ChromaDB | Open source |
| Qdrant | Open source / cloud |
| Weaviate | Open source / cloud |
| Pinecone | Cloud (third party) |

---

## 10. Diferencias clave entre modelos

| Característica | `gemini-embedding-001` | `gemini-embedding-2` |
|---|---|---|
| Modalidades | Solo texto | Texto, imagen, PDF |
| Task type | Parámetro `task_type` | Instrucción en el prompt |
| Múltiples inputs | Embeddings individuales por string | Embedding agregado (usa `Content` para separar) |
| Normalización automática | Solo en 3072 dims | En todas las dimensiones |
| Compatibilidad de espacios | ❌ Incompatible con embedding-2 | ❌ Incompatible con embedding-001 |

---

## Casos de uso principales

- **RAG (Retrieval-Augmented Generation):** indexar documentos para mejorar respuestas de LLMs.
- **Búsqueda semántica:** encontrar textos o imágenes similares a una consulta.
- **Clasificación:** categorizar texto o imágenes automáticamente.
- **Clustering:** agrupar contenido por similitud conceptual.
- **Detección de anomalías:** identificar outliers comparando grupos de embeddings.
- **Búsqueda cross-modal:** buscar imágenes con texto o texto con imágenes.