from fastapi import FastAPI, APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from authlib.jose import jwt
import os
import requests
from authlib.jose import JsonWebKey, JsonWebToken
import base64
import json
from starlette.middleware.sessions import SessionMiddleware
import os
import httpx
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse
from google.oauth2 import id_token
from dotenv import load_dotenv
from google.auth.transport import requests
from fastapi.responses import RedirectResponse
from urllib.parse import urlencode

router = APIRouter()

# Load env
config = Config(".env")
oauth = OAuth(config)

oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile',
    },
)
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

@router.get("/api/auth/signin")
async def login(request: Request):
    redirect_uri = "http://127.0.0.1:8000/auth/callback"
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/api/auth/session")
async def get_session(request: Request):
    user_name = request.session.get("user_name")  # Ім'я, яке ти зберігаєш у сесії при логіні
    if not user_name:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    return {"user_name": user_name}

@router.get("/api/auth/error")
async def auth_error(request: Request, error_message: str):
    """
    Endpoint to display an authentication error.
    """
    raise HTTPException(status_code=401, detail=error_message)

@router.get("/api/auth/providers")
async def get_providers(request: Request):
    """
    Endpoint to return available authentication providers.
    """
    return {"providers": ["google"]}

import logging
logger = logging.getLogger(__name__)

@router.post("/api/auth/_log")
async def auth_log(request: Request):
    """
    Endpoint to log authentication information via POST.
    """
    logger.info("Authentication log endpoint hit via POST")
    return {"message": "Logged authentication information"}

@router.get("/auth/callback", name="auth_callback")
async def auth_callback(code: str, request: Request):
    token_request_uri = "https://oauth2.googleapis.com/token"
    data = {
        'code': code,
        'client_id': GOOGLE_CLIENT_ID,
        'client_secret': GOOGLE_CLIENT_SECRET,
        'redirect_uri': request.url_for('auth_callback'),
        'grant_type': 'authorization_code',
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(token_request_uri, data=data)
        response.raise_for_status()
        token_response = response.json()

    id_token_value = token_response.get('id_token')
    if not id_token_value:
        raise HTTPException(status_code=400, detail="Missing id_token in response.")

    try:
        id_info = id_token.verify_oauth2_token(id_token_value, requests.Request(), GOOGLE_CLIENT_ID)

        request.session['user_name'] = id_info.get('name')
        request.session['email'] = id_info.get('email')

        params = {
        "email": id_info["email"],
        "name": id_info.get("name"),
         "picture": id_info.get("picture"),
         # Не передавай секретні дані в URL!
        }
        frontend_url = "http://localhost:3000?" + urlencode(params)

        return RedirectResponse(frontend_url)
        return {
        "email": id_info["email"],
        "name": id_info["name"],
        "picture": id_info.get("picture"),
    }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid id_token: {str(e)}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=e)



# Step 1: Decode JWT header to get 'kid'
def decode_jwt_header(token):
    header_b64 = token.split('.')[0]
    padding = '=' * (-len(header_b64) % 4)
    header_bytes = base64.urlsafe_b64decode(header_b64 + padding)
    return json.loads(header_bytes)

# Add ping endpoint
@router.get("/api/ping")
async def ping():
    return "pong"   

@router.post("/auth/google")
async def auth_google(data: dict):
    token = data.get("access_token")
    if not token:
        raise HTTPException(status_code=400, detail="No token")

    try:
        id_info = id_token.verify_oauth2_token(token, google_requests.Request(), GOOGLE_CLIENT_ID)
        return {"success": True, "user": id_info}
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))
    

# Create and configure the FastAPI app instance
app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware


# CORS MUST be applied before routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # exact match!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET_KEY", "defaultsecret"))
app.include_router(router)
