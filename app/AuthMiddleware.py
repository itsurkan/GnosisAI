from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        token = request.headers.get("Authorization")

        user = None
        if token and token.startswith("Bearer "):
            token = token.replace("Bearer ", "")
            try:
                # Validate token with Google
                id_info = id_token.verify_oauth2_token(token, google_requests.Request(), GOOGLE_CLIENT_ID)
                user = {
                    "id": id_info["sub"],
                    "email": id_info["email"],
                    "name": id_info["name"],
                    "picture": id_info.get("picture")
                }
            except Exception as e:
                print(f"Token validation error: {e}")

        request.state.user = user
        if hasattr(request, 'session'):
            return await call_next(request)
        else:
            return await call_next(request)
