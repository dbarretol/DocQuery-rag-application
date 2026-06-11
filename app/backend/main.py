import logging
import sys
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from starlette.requests import Request
from pythonjsonlogger import json

# Setup JSON Logging for Cloud Run compatibility
logger = logging.getLogger("uvicorn")
handler = logging.StreamHandler(sys.stdout)
formatter = json.JsonFormatter('%(asctime)s %(name)s %(levelname)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

app = FastAPI(title="Multimodal RAG Platform")

Instrumentator().instrument(app).expose(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="app/templates")

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    logger.info("Received file", extra={"filename": file.filename})
    return {"message": "Document accepted for processing", "filename": file.filename}

@app.get("/documents")
async def list_documents():
    return {"documents": []}

@app.delete("/documents/{doc_id}")
async def delete_document(doc_id: str):
    logger.info("Deleting document", extra={"doc_id": doc_id})
    return {"message": f"Document {doc_id} deleted"}

@app.post("/chat")
async def chat(data: dict):
    question = data.get("question")
    logger.info("Received chat query", extra={"question": question})
    return {"answer": f"Stub response for: {question}"}
