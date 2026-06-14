import os
from dotenv import load_dotenv
import shutil
from fastapi import FastAPI, UploadFile, File, BackgroundTasks, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from prometheus_fastapi_instrumentator import Instrumentator
from starlette.requests import Request
from app.backend.rag.ingest import ingest_document
from app.backend.rag.retrieval import retrieve_context
from app.backend.rag.generation import generate_answer, generate_suggestions
from app.backend.storage.gcs import download_index, upload_index
from app.backend.storage.chroma import get_chroma_client
from app.backend.config_loader import config, settings
from app.backend.api_models import (
    ChatRequest, ChatResponse, SuggestionRequest, SuggestionResponse,
    UploadResponse, DocumentStatusResponse, KnowledgeBaseResponse, PassageResponse,
    GCSConfigRequest
)
from app.backend.storage.models import storage_config
from app.backend.middleware import CorrelationIDMiddleware
from app.backend.logger_setup import setup_logger

load_dotenv()

# Setup Logging
logger = setup_logger("uvicorn")
logger.info("Logging initialized with Correlation ID support")

app = FastAPI(title="Multimodal RAG Platform")

app.add_middleware(CorrelationIDMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (favicon, etc.)
app.mount("/static", StaticFiles(directory="app/templates/static"), name="static")

templates = Jinja2Templates(directory="app/templates")

# Temporary storage for uploaded files to be processed
UPLOAD_DIR = "data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.on_event("startup")
async def startup_event():
    # download_index(settings.CHROMA_PATH)
    pass

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/config")
async def get_config():
    logger.info("Config requested")
    return config

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.post("/upload", response_model=UploadResponse)
async def upload_document(
    background_tasks: BackgroundTasks, 
    file: UploadFile = File(...),
    generation_model: str = Form(None),
    embedding_model: str = Form(None)
):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    background_tasks.add_task(ingest_document, file_path, file.filename, generation_model, embedding_model)
    
    logger.info(f"Received file, queued for processing: {file.filename} (gen: {generation_model}, emb: {embedding_model})")
    return {"message": "Document accepted for processing", "filename": file.filename}

@app.get("/document-status/{filename}", response_model=DocumentStatusResponse)
async def get_document_status(filename: str):
    status_path = os.path.join(UPLOAD_DIR, f"{filename}.status")
    
    if os.path.exists(status_path):
        with open(status_path, "r", encoding="utf-8") as f:
            status = f.read().strip()
            return {"status": status}
            
    return {"status": "NOT_FOUND"}

@app.get("/knowledge-base", response_model=KnowledgeBaseResponse)
async def get_knowledge_base():
    chroma_client = get_chroma_client()
    collection = chroma_client.get_or_create_collection(name=storage_config.collection_name)
    
    # Get all unique filenames from metadatas
    results = collection.get(include=["metadatas"])
    metadatas = results["metadatas"]
    
    unique_docs = {}
    for meta in metadatas:
        filename = meta.get("filename")
        if filename and filename not in unique_docs:
            unique_docs[filename] = {
                "filename": filename,
                "content_type": meta.get("content_type", "unknown")
            }
            
    return {"documents": list(unique_docs.values())}

@app.delete("/documents/{filename}")
async def delete_document(filename: str):
    logger.info(f"Deleting document: {filename}")
    
    # 1. Remove from ChromaDB
    chroma_client = get_chroma_client()
    collection = chroma_client.get_or_create_collection(name=storage_config.collection_name)
    
    # Delete based on filename in metadata
    collection.delete(where={"filename": filename})
    
    # 2. Remove files
    file_path = os.path.join(UPLOAD_DIR, filename)
    status_path = os.path.join(UPLOAD_DIR, f"{filename}.status")
    
    if os.path.exists(file_path):
        os.remove(file_path)
    if os.path.exists(status_path):
        os.remove(status_path)
        
    return {"message": f"Document {filename} deleted"}

@app.post("/chat", response_model=ChatResponse)
async def chat(data: ChatRequest):
    question = data.question
    generation_model = data.generation_model
    language = data.language
    
    logger.info(f"Received chat query: {question} (gen: {generation_model}, lang: {language})")
    
    # Retrieval
    context = retrieve_context(question)
    
    # Generation
    response = generate_answer(question, context, generation_model, language)
    
    # Log context sources for observability
    source_ids = [s.id for s in response.sources]
    logger.info(f"Chat query completed. Context sources used: {source_ids}")
    
    return response

@app.post("/chat/suggestions", response_model=SuggestionResponse)
async def chat_suggestions(data: SuggestionRequest):
    question = data.question
    answer = data.answer
    language = data.language
    
    logger.info(f"Generating suggestions for: {question}")
    
    # Retrieval (to get context for suggestions)
    context = retrieve_context(question)
    
    # Generation
    suggestions = generate_suggestions(question, answer, context, language)
    
    return {"suggestions": suggestions}

@app.get("/passage/{passage_id}", response_model=PassageResponse)
async def get_passage(passage_id: str):
    logger.info(f"Retrieving passage: {passage_id}")
    chroma_client = get_chroma_client()
    collection = chroma_client.get_or_create_collection(name=storage_config.collection_name)
    
    result = collection.get(ids=[passage_id])
    
    if not result["documents"]:
        raise HTTPException(status_code=404, detail="Passage not found")
        
    content = result["documents"][0]
    metadata = result["metadatas"][0]
    
    return {
        "content": content,
        "metadata": metadata,
        "type": metadata.get("content_type", "text")
    }

@app.post("/sync/upload")
async def sync_upload(data: GCSConfigRequest):
    upload_index(settings.CHROMA_PATH, data.bucket_name)
    return {"message": "Sync upload completed"}

@app.post("/sync/download")
async def sync_download(data: GCSConfigRequest):
    download_index(settings.CHROMA_PATH, data.bucket_name)
    return {"message": "Sync download completed"}

# Instrumentator at the end
Instrumentator().instrument(app).expose(app)
