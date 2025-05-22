from fastapi import FastAPI, UploadFile, File, Header, HTTPException, APIRouter
from app.azure_storage import upload_file
from starlette.middleware.sessions import SessionMiddleware
import os
from fastapi.middleware.cors import CORSMiddleware
from authlib.jose import jwt
from app.tokenDecoder import decode_jwt_payload
from app.emailToTenant import email_to_tenant
from app.pinecone import add_to_index

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
    await add_to_index(file, token["email"])
    return await upload_file(file, token["email"])

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



