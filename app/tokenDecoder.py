import base64
import json

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
    


from fastapi import HTTPException
import base64
import json

def decode_jwt_payload(authorization: str) -> dict:
    """
    Decodes the payload (body) of a JWT token and returns it as a dictionary.
    Assumes the token is in JWT format and may include 'Bearer ' prefix.
    """
    if authorization is None:
        raise HTTPException(status_code=401, detail="Authorization header is missing")

    token = authorization
    if token.startswith("Bearer "):
        token = token[len("Bearer "):]

    try:
        payload_b64 = token.split('.')[1]
        padded = payload_b64 + '=' * (-len(payload_b64) % 4)
        payload_bytes = base64.urlsafe_b64decode(padded)
        return json.loads(payload_bytes)
    except (IndexError, ValueError, json.JSONDecodeError, base64.binascii.Error) as e:
        raise ValueError(f"Invalid JWT token payload: {e}")
