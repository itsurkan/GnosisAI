from fastapi import FastAPI, UploadFile, File, Header, HTTPException
import logging
from app.azure_storage import upload_file

app = FastAPI()


@app.post("/upload/")
async def upload_file_endpoint(
    file: UploadFile = File(...)
):
     return await upload_file(file)

@app.delete("/delete/{file_id}")
async def delete_file_endpoint(file_id: str):
     from app.azure_storage import delete_file
     return await delete_file(file_id)
