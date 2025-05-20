from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from authlib.jose import jwt
import os
import requests
from authlib.jose import JsonWebKey, JsonWebToken
import base64
import json

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
        'token_endpoint_auth_method': 'client_secret_post'
    },
)

@router.get("/auth/login")
async def login(request: Request):
    redirect_uri = os.getenv("GOOGLE_REDIRECT_URI")
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/auth/callback")
async def auth_callback(request: Request):
    token = await oauth.google.authorize_access_token(request)
    id_token = token.get("id_token")
    if not id_token:
        raise HTTPException(status_code=400, detail="Missing id_token in token")

    
    header = decode_jwt_header(id_token)
    kid = header.get('kid')
    
    # Step 2: Fetch Google's JWKS
    jwks_url = "https://www.googleapis.com/oauth2/v3/certs"
    jwks_response = requests.get(jwks_url).json()

    # Step 3: Find the key with matching kid
    jwks = JsonWebKey.import_key_set(jwks_response)
    key = jwks.find_by_kid(kid)
    if key is None:
        raise Exception("Public key not found for kid")

    # Step 4: Verify the JWT
    jwt_obj = JsonWebToken(['RS256'])
    claims = jwt_obj.decode(id_token, key)
    claims.validate()  # optional, validates exp, ia
    
    return {
        "email": claims["email"],
        "name": claims["name"],
        "picture": claims.get("picture"),
    }

# Step 1: Decode JWT header to get 'kid'
def decode_jwt_header(token):
    header_b64 = token.split('.')[0]
    padding = '=' * (-len(header_b64) % 4)
    header_bytes = base64.urlsafe_b64decode(header_b64 + padding)
    return json.loads(header_bytes)