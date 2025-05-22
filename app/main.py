from fastapi import FastAPI, UploadFile, File, Header, HTTPException, APIRouter
from app.azure_storage import upload_file
from starlette.middleware.sessions import SessionMiddleware
import os
from fastapi.middleware.cors import CORSMiddleware
from authlib.jose import jwt
from app.tokenDecoder import decode_jwt_payload
from app.emailToTenant import email_to_tenant
from app.pinecone import add_to_index
from pdfminer.high_level import extract_text as extract_text_pdf
import docx

def chunk_text(text, chunk_size=200, chunk_overlap=50):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        if end > len(text):
            end = len(text)
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - chunk_overlap
    return chunks

app = FastAPI(
    title="Your API Title",
    description="Your API Description",
    version="1.0.0",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = APIRouter()
app.include_router(router)
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET_KEY", "defaultsecret"))

@app.post("/upload/")
async def upload_file_endpoint(file: UploadFile = File(...), authorization: str = Header(None)):
    token = decode_jwt_payload(authorization)
    index = email_to_tenant(token["email"])
    file_type = file.filename.split(".")[-1].lower()
    file_content = ""

    if file_type == "pdf":
        file_content = extract_text_pdf(file.file)
    elif file_type == "docx":
        doc = docx.Document(file.file)
        file_content = "\n".join([p.text for p in doc.paragraphs])
    elif file_type == "txt":
        file_content = (await file.read()).decode()
    else:
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF, DOCX, and TXT files are supported.")

    chunks = chunk_text(file_content)
    await add_to_index(chunks, index)
    return {"filename": file.filename, "file_type": file_type, "file_content": file_content}

@app.delete("/delete/{file_id}")
async def delete_file_endpoint(file_id: str, authorization: str = Header(None)):
     token = decode_jwt_payload(authorization)
     from app.azure_storage import delete_file
     return await delete_file(file_id, token["email"])

@app.get("/files")
async def get_user_files(authorization: str = Header(None)):
    from app.azure_storage import list_files
    token = decode_jwt_payload(authorization)
    return await list_files(token["email"])

@app.post("/query/")
async def query_index(query: str, authorization: str = Header(None)):
    token = decode_jwt_payload(authorization)
    email = token["email"]
    relevant_chunks = await query_index(query, email)
    return {"query": query, "email": email, "results": relevant_chunks}
