import os
from dotenv import load_dotenv
import logging
import sys
import shutil
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
from app.backend.rag.generation import generate_answer
from app.backend.storage.gcs import download_index
from app.backend.storage.chroma import get_chroma_client
from app.backend.config_loader import config

load_dotenv()
# Setup JSON Logging for Cloud Run compatibility
logger = logging.getLogger("uvicorn")
handler = logging.StreamHandler(sys.stdout)
formatter = json.JsonFormatter(
    '%(asctime)s %(name)s %(levelname)s %(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

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

@app.delete("/documents/{filename}")
async def delete_document(filename: str):
    logger.info(f"Deleting document: {filename}")
    
    # 1. Remove from ChromaDB
    chroma_client = get_chroma_client()
    collection = chroma_client.get_or_create_collection(name="documents")
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

# Instrumentator at the end
Instrumentator().instrument(app).expose(app)
