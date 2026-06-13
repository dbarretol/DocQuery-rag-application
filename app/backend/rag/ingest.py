import os
import fitz
from typing import List
import logging
import io
from PIL import Image as PILImage
from app.backend.storage.chroma import get_chroma_client
from app.backend.storage.gcs import upload_index
from app.backend.config_loader import get_generation_model, get_embedding_model, get_prompt, settings
from app.backend.rag.utils import get_client
from app.backend.rag.retry_config import retry_on_api_errors
from app.backend.rag.models import ChunkMetadata, IngestionStatus

logger = logging.getLogger("uvicorn")

def chunk_text(text: str, chunk_size: int = 500) -> List[str]:
    """Simple chunking by character count (approx tokens)."""
    char_limit = chunk_size * 4
    return [text[i:i + char_limit] for i in range(0, len(text), char_limit)]

async def describe_image(image_bytes: bytes, model_name: str = None) -> str:
    """Generate image description using Gemini."""
    client = get_client()
    image = PILImage.open(io.BytesIO(image_bytes))
    
    @retry_on_api_errors
    def _generate():
        return client.models.generate_content(
            model=model_name or get_generation_model(),
            contents=[get_prompt("image_description"), image]
        )
        
    response = _generate()
    return response.text

def set_status(filename: str, status: IngestionStatus):
    status_path = os.path.join("data/uploads", f"{filename}.status")
    with open(status_path, "w", encoding="utf-8") as f:
        f.write(status.value)

async def ingest_document(file_path: str, filename: str, generation_model: str = None, embedding_model: str = None):
    set_status(filename, IngestionStatus.PROCESSING)
    logger.info(f"--- STARTING INGESTION: {filename} ---")
    logger.info(f"Models configured [gen: {generation_model}, emb: {embedding_model}]")

    embedding_model_name = embedding_model or get_embedding_model()
    ext = os.path.splitext(filename)[1].lower()
    logger.info(f"File extension detected: {ext}")

    # Validation for text-only model
    if embedding_model_name == "gemini-embedding-001" and ext not in [".md", ".txt", ".csv"]:
        error_msg = "Unsupported file type for text-only model"
        set_status(filename, IngestionStatus.ERROR)
        logger.warning(f"REJECTED: File {filename} for model {embedding_model_name}. Reason: {error_msg}.")
        return "ERROR"

    client = get_client()
    chroma_client = get_chroma_client()
    collection = chroma_client.get_or_create_collection(name="documents")
    logger.info("ChromaDB collection accessed/created.")

    @retry_on_api_errors
    def _embed(chunk):
        return client.models.embed_content(model=embedding_model_name, contents=chunk)

    try:
        if ext == ".pdf":
            logger.info("Processing PDF...")
            doc = fitz.open(file_path)
            total_pages = len(doc)
            logger.info(f"PDF opened. Total pages: {total_pages}")

            for page_num in range(total_pages):
                logger.info(f"Processing page {page_num + 1}/{total_pages}")
                page = doc[page_num]
                text = page.get_text()
                chunks = chunk_text(text)
                logger.info(f"Page {page_num + 1} segmented into {len(chunks)} text chunks")

                for i, chunk in enumerate(chunks):
                    logger.debug(f"Embedding text chunk {i+1}...")
                    response = _embed(chunk)
                    embedding = response.embeddings[0].values
                    
                    metadata = ChunkMetadata(
                        filename=filename,
                        page=page_num + 1,
                        chunk_index=i,
                        content_type="text"
                    )
                    
                    collection.add(
                        documents=[chunk],
                        metadatas=[metadata.model_dump()],
                        ids=[f"{filename}_{page_num}_{i}_text"],
                        embeddings=[embedding]
                    )

                image_list = page.get_images(full=True)
                logger.info(f"Page {page_num + 1} has {len(image_list)} images")

                for img_index, img in enumerate(image_list):
                    logger.info(f"Processing image {img_index + 1}/{len(image_list)} on page {page_num + 1}")
                    xref = img[0]
                    pix = fitz.Pixmap(doc, xref)
                    if pix.colorspace and pix.colorspace.n > 3:
                        pix = fitz.Pixmap(fitz.csRGB, pix)
                    description = await describe_image(pix.tobytes("png"), generation_model)
                    logger.debug("Image described.")

                    response = _embed(description)
                    embedding = response.embeddings[0].values
                    
                    metadata = ChunkMetadata(
                        filename=filename,
                        page=page_num + 1,
                        img_index=img_index,
                        content_type="image"
                    )
                    
                    collection.add(
                        documents=[description],
                        metadatas=[metadata.model_dump()],
                        ids=[f"{filename}_{page_num}_{img_index}_image"],
                        embeddings=[embedding]
                    )
            logger.info("PDF processing completed successfully.")

        elif ext in [".md", ".txt"]:
            logger.info("Processing Text/Markdown file...")
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
            chunks = chunk_text(text)
            logger.info(f"File segmented into {len(chunks)} chunks")
            for i, chunk in enumerate(chunks):
                response = _embed(chunk)
                embedding = response.embeddings[0].values
                
                metadata = ChunkMetadata(
                    filename=filename,
                    page=1,
                    chunk_index=i,
                    content_type="markdown"
                )
                
                collection.add(
                    documents=[chunk],
                    metadatas=[metadata.model_dump()],
                    ids=[f"{filename}_{i}_md"],
                    embeddings=[embedding]
                )
            logger.info("Text processing completed.")

        elif ext in [".png", ".jpg", ".jpeg"]:
            logger.info("Processing Image file...")
            with open(file_path, "rb") as f:
                img_bytes = f.read()
            description = await describe_image(img_bytes, generation_model)

            response = _embed(description)
            embedding = response.embeddings[0].values
            
            metadata = ChunkMetadata(
                filename=filename,
                page=1,
                content_type="image"
            )
            
            collection.add(
                documents=[description],
                metadatas=[metadata.model_dump()],
                ids=[f"{filename}_image"],
                embeddings=[embedding]
            )
            logger.info("Image processing completed.")
        else:
            set_status(filename, IngestionStatus.ERROR)
            logger.warning(f"UNSUPPORTED: File {filename} has extension {ext}")
            return "ERROR"

        set_status(filename, IngestionStatus.INDEXED)
        logger.info(f"--- INGESTION SUCCESSFUL: {filename} ---")
        upload_index(settings.CHROMA_PATH)
        return "INDEXED"

    except Exception as e:
        set_status(filename, IngestionStatus.ERROR)
        logger.error(f"--- INGESTION FAILED: {filename} ---")
        logger.exception(f"Details: {e}")
        return "ERROR"

