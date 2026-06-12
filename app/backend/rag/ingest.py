import os
import fitz
from google import genai
from typing import List
import logging
import io
from PIL import Image as PILImage
from app.backend.storage.chroma import get_chroma_client
from app.backend.storage.gcs import upload_index
from app.backend.config_loader import get_generation_model, get_embedding_model

logger = logging.getLogger("uvicorn")

# Configure Gemini
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY", "dummy_key"))

def chunk_text(text: str, chunk_size: int = 500) -> List[str]:
    """Simple chunking by character count (approx tokens)."""
    char_limit = chunk_size * 4
    return [text[i:i + char_limit] for i in range(0, len(text), char_limit)]

async def describe_image(image_bytes: bytes, model_name: str = None) -> str:
    """Generate image description using Gemini."""
    image = PILImage.open(io.BytesIO(image_bytes))
    response = client.models.generate_content(
        model=model_name or get_generation_model(),
        contents=["Explain what is going on in the image.", image]
    )
    return response.text

async def ingest_document(file_path: str, filename: str, generation_model: str = None, embedding_model: str = None):
    logger.info(f"Processing document: {filename} with models [gen: {generation_model}, emb: {embedding_model}]")
    
    chroma_client = get_chroma_client()
    collection = chroma_client.get_or_create_collection(name="documents")
    embedding_model_name = embedding_model or get_embedding_model()
    
    try:
        # Determine content type
        content_type = "pdf" if filename.lower().endswith(".pdf") else "markdown"
        
        if content_type == "pdf":
            doc = fitz.open(file_path)
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                chunks = chunk_text(text)
                
                for i, chunk in enumerate(chunks):
                    response = client.models.embed_content(model=embedding_model_name, contents=chunk)
                    embedding = response.embeddings[0].values
                    collection.add(
                        documents=[chunk],
                        metadatas=[{"filename": filename, "page": page_num, "chunk_index": i, "content_type": "text", "status": "INDEXED"}],
                        ids=[f"{filename}_{page_num}_{i}_text"],
                        embeddings=[embedding]
                    )

                image_list = page.get_images(full=True)
                for img_index, img in enumerate(image_list):
                    xref = img[0]
                    pix = fitz.Pixmap(doc, xref)
                    if pix.colorspace and pix.colorspace.n > 3: pix = fitz.Pixmap(fitz.csRGB, pix)
                    description = await describe_image(pix.tobytes("png"), generation_model)
                    
                    response = client.models.embed_content(model=embedding_model_name, contents=description)
                    embedding = response.embeddings[0].values
                    collection.add(
                        documents=[description],
                        metadatas=[{"filename": filename, "page": page_num, "img_index": img_index, "content_type": "image", "status": "INDEXED"}],
                        ids=[f"{filename}_{page_num}_{img_index}_image"],
                        embeddings=[embedding]
                    )
        else:
            # Markdown extraction
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
            chunks = chunk_text(text)
            for i, chunk in enumerate(chunks):
                response = client.models.embed_content(model=embedding_model_name, contents=chunk)
                embedding = response.embeddings[0].values
                collection.add(
                    documents=[chunk],
                    metadatas=[{"filename": filename, "page": 0, "chunk_index": i, "content_type": "markdown", "status": "INDEXED"}],
                    ids=[f"{filename}_{i}_md"],
                    embeddings=[embedding]
                )
        
        logger.info(f"Successfully indexed document: {filename}")
        upload_index(os.getenv("CHROMA_PATH", "./data/chroma"))
        return "INDEXED"
        
    except Exception as e:
        logger.error(f"Error processing document {filename}: {e}")
        return "ERROR"
