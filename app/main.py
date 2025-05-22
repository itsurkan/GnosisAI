from fastapi import FastAPI, UploadFile, File, Header, HTTPException, APIRouter
from app.azure_storage import upload_file
from starlette.middleware.sessions import SessionMiddleware
import os
from fastapi.middleware.cors import CORSMiddleware
from app.auth import get_user_email
from authlib.jose import jwt
import base64
import json

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
    # allow_origins=["http://localhost:3000", "http://127.0.0.1:3000","https://6000-firebase-studio-1747911302932.cluster-l6vkdperq5ebaqo3qy4ksvoqom.cloudworkstations.dev",
    #                "https://000-firebase-studio-1747911302932.cluster-l6vkdperq5ebaqo3qy4ksvoqom.cloudworkstations.dev",
    #                "https://c987-194-183-168-157.ngrok-free.app"],  
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


router = APIRouter()
app.include_router(router)
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET_KEY", "defaultsecret"))

@app.post("/upload/")
async def upload_file_endpoint(
    file: UploadFile = File(...),
    authorization: str = Header(None)
):
    token = decode_jwt_payload(authorization)
    return await upload_file(file, token["email"])

@app.delete("/delete/{file_id}")
async def delete_file_endpoint(file_id: str):
     from app.azure_storage import delete_file
     return await delete_file(file_id)


def decode_jwt_header(token: str) -> dict:
    """
    Decodes the header of a JWT token and returns it as a dictionary.
    Supports tokens prefixed with 'Bearer '.
    """
    if token.startswith("Bearer "):
        token = token[len("Bearer "):]

    try:
        header_b64 = token.split('.')[0]
        # Pad base64 if needed
        padded = header_b64 + '=' * (-len(header_b64) % 4)
        header_bytes = base64.urlsafe_b64decode(padded)
        return json.loads(header_bytes)
    except (IndexError, ValueError, json.JSONDecodeError, base64.binascii.Error) as e:
        raise ValueError(f"Invalid JWT token format: {e}")
    

    import base64
import json

def decode_jwt_payload(token: str) -> dict:
    """
    Decodes the payload (body) of a JWT token and returns it as a dictionary.
    Assumes the token is in JWT format and may include 'Bearer ' prefix.
    """
    if token.startswith("Bearer "):
        token = token[len("Bearer "):]

    try:
        payload_b64 = token.split('.')[1]
        padded = payload_b64 + '=' * (-len(payload_b64) % 4)
        payload_bytes = base64.urlsafe_b64decode(padded)
        return json.loads(payload_bytes)
    except (IndexError, ValueError, json.JSONDecodeError, base64.binascii.Error) as e:
        raise ValueError(f"Invalid JWT token payload: {e}")
