from fastapi import FastAPI, UploadFile, File, Header, HTTPException
from app.azure_storage import upload_file
from app.auth import router as auth_router
from starlette.middleware.sessions import SessionMiddleware
import os
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # дозволь фронтенд
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_router)
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET_KEY", "defaultsecret"))

@app.post("/upload/")
async def upload_file_endpoint(
    file: UploadFile = File(...)
):
     return await upload_file(file)

@app.delete("/delete/{file_id}")
async def delete_file_endpoint(file_id: str):
     from app.azure_storage import delete_file
     return await delete_file(file_id)
