from fastapi import HTTPException, Header
import jwt

def get_user_email(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header is missing")

    try:
        token = authorization.split(" ")[1]
        payload = jwt.decode(token, "secret", algorithms=["HS256"])
        return payload.get("email")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
