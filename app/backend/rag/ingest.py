import os
import fitz
import google.generativeai as genai
from typing import List
import logging
import io
from PIL import Image as PILImage
from app.backend.storage.chroma import get_chroma_client
from app.backend.config_loader import get_generation_model, get_embedding_model

logger = logging.getLogger("uvicorn")

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
# Using dynamic configuration
model = genai.GenerativeModel(get_generation_model())

def chunk_text(text: str, chunk_size: int = 500) -> List[str]:
    """Simple chunking by character count (approx tokens)."""
    # Simple estimation: 1 token ~ 4 chars
    char_limit = chunk_size * 4
    return [text[i:i + char_limit] for i in range(0, len(text), char_limit)]

async def describe_image(image_bytes: bytes) -> str:
    """Generate image description using Gemini."""
    image = PILImage.open(io.BytesIO(image_bytes))
    response = model.generate_content(["Explain what is going on in the image.", image])
    return response.text

async def ingest_document(file_path: str, filename: str):
    logger.info(f"Processing document: {filename}")
    
    # 1. Extraction
    doc = fitz.open(file_path)
    chroma_client = get_chroma_client()
    collection = chroma_client.get_or_create_collection(name="documents")
    
    embedding_model_name = get_embedding_model()
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        
        # Text extraction
        text = page.get_text()
        chunks = chunk_text(text)
        
        for i, chunk in enumerate(chunks):
            # Using dynamic embedding model
            embedding = genai.embed_content(
                model=embedding_model_name,
                content=chunk,
                task_type="retrieval_document"
            )["embedding"]
            
            collection.add(
                documents=[chunk],
                metadatas=[{"filename": filename, "page": page_num, "chunk_index": i, "type": "text"}],
                ids=[f"{filename}_{page_num}_{i}_text"],
                embeddings=[embedding]
            )

        # Image extraction and description
        image_list = page.get_images(full=True)
        for img_index, img in enumerate(image_list):
            xref = img[0]
            pix = fitz.Pixmap(doc, xref)
            if pix.colorspace and pix.colorspace.n > 3:
                pix = fitz.Pixmap(fitz.csRGB, pix)
            image_bytes = pix.tobytes("png")
            
            description = await describe_image(image_bytes)
            
            embedding = genai.embed_content(
                model=embedding_model_name,
                content=description,
                task_type="retrieval_document"
            )["embedding"]
            
            collection.add(
                documents=[description],
                metadatas=[{"filename": filename, "page": page_num, "img_index": img_index, "type": "image"}],
                ids=[f"{filename}_{page_num}_{img_index}_image"],
                embeddings=[embedding]
            )
    
    logger.info(f"Successfully indexed document: {filename}")
    return "INDEXED"
