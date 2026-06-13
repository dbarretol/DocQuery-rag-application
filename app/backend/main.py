import os
from dotenv import load_dotenv
import logging
import sys
import shutil
import datetime
from fastapi import FastAPI, UploadFile, File, BackgroundTasks, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from prometheus_fastapi_instrumentator import Instrumentator
from starlette.requests import Request
from pythonjsonlogger import json
from app.backend.rag.ingest import ingest_document
from app.backend.rag.retrieval import retrieve_context
from app.backend.rag.generation import generate_answer, generate_suggestions
from app.backend.storage.gcs import download_index
from app.backend.storage.chroma import get_chroma_client
from app.backend.config_loader import config

load_dotenv()

# Setup Logging
os.makedirs("logs", exist_ok=True)
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
log_filename = f"logs/app_{timestamp}.log"

logger = logging.getLogger("uvicorn")
# Remove existing handlers to avoid duplicates
for handler in logger.handlers[:]:
    logger.removeHandler(handler)

# File Handler
file_handler = logging.FileHandler(log_filename)
file_handler.setFormatter(logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s'))
logger.addHandler(file_handler)

# Console Handler for Cloud Run compatibility
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(json.JsonFormatter('%(asctime)s %(name)s %(levelname)s %(message)s'))
logger.addHandler(console_handler)

logger.setLevel(logging.INFO)
logger.info(f"Logging initialized. Log file: {log_filename}")

app = FastAPI(title="Multimodal RAG Platform")

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
    download_index(os.getenv("CHROMA_PATH", "./data/chroma"))

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

@app.post("/upload")
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

@app.get("/document-status/{filename}")
async def get_document_status(filename: str):
    status_path = os.path.join(UPLOAD_DIR, f"{filename}.status")
    
    if os.path.exists(status_path):
        with open(status_path, "r", encoding="utf-8") as f:
            status = f.read().strip()
            return {"status": status}
            
    return {"status": "NOT_FOUND"}

@app.get("/knowledge-base")
async def get_knowledge_base():
    chroma_client = get_chroma_client()
    collection = chroma_client.get_or_create_collection(name="documents")
    
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
    collection = chroma_client.get_or_create_collection(name="documents")
    
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

@app.post("/chat")
async def chat(data: dict):
    question = data.get("question")
    generation_model = data.get("generation_model")
    language = data.get("language", "Spanish")
    
    if not question:
        return {"error": "Question is required"}
        
    logger.info(f"Received chat query: {question} (gen: {generation_model}, lang: {language})")
    
    # Retrieval
    context = retrieve_context(question)
    
    # Generation
    response = generate_answer(question, context, generation_model, language)
    
    return response

@app.post("/chat/suggestions")
async def chat_suggestions(data: dict):
    question = data.get("question")
    answer = data.get("answer")
    language = data.get("language", "Spanish")
    
    if not question or not answer:
        return {"error": "Question and answer are required"}
        
    logger.info(f"Generating suggestions for: {question}")
    
    # Retrieval (to get context for suggestions)
    context = retrieve_context(question)
    
    # Generation
    suggestions = generate_suggestions(question, answer, context, language)
    
    return {"suggestions": suggestions}

# Instrumentator at the end
Instrumentator().instrument(app).expose(app)
