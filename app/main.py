from fastapi import FastAPI, UploadFile, File, Header, HTTPException, APIRouter
from app.azure_storage import upload_file
from starlette.middleware.sessions import SessionMiddleware
import os
from fastapi.middleware.cors import CORSMiddleware
from authlib.jose import jwt
from app.tokenDecoder import decode_jwt_payload
from app.emailToTenant import email_to_tenant
from app.pinecone import add_to_index, query_index_pinecone
from pdfminer.high_level import extract_text as extract_text_pdf
import docx
import logging
import re
logger = logging.getLogger(__name__)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader, UnstructuredMarkdownLoader, UnstructuredFileLoader


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

    logger.info(f"File type: {file_type}")
    logger.info(f"File content length: {len(file_content)}")

    text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=500,
                chunk_overlap=100,
                length_function=len,
                is_separator_regex=False,
            )
    texts = text_splitter.split_text(file_content)
    logger.info(f"Number of chunks: {len(texts)}")

    await add_to_index(texts, index)
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

@app.get("/query")
async def query_index(query: str, authorization: str = Header(None)):
    token = decode_jwt_payload(authorization)
    tenant = email_to_tenant(token["email"])
    relevant_chunks = await query_index_pinecone(query, tenant)
    return {"query": query, "email": tenant, "results": relevant_chunks}
