from fastapi import UploadFile, File, HTTPException
from azure.storage.blob import BlobServiceClient, ContainerClient
import os
import logging
import uuid

AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)

def get_or_create_container(container_name: str) -> ContainerClient:
    container_client = blob_service_client.get_container_client(container_name)
    try:
        container_client.get_container_properties()
    except Exception:
        container_client = blob_service_client.create_container(container_name)
    return container_client

async def upload_file(file: UploadFile = File(...)):
    tenant = "default"
    container_name = tenant.lower()

    # Перевірка валідності імені контейнера
    if not container_name.replace('-', '').isalnum():
        raise HTTPException(status_code=400, detail="Invalid tenant/container name")

    try:
        container_client = get_or_create_container(container_name)
        blob_name = str(uuid.uuid4()) + "_" + file.filename
        blob_client = container_client.get_blob_client(blob_name)

        content = await file.read()
        blob_client.upload_blob(content, overwrite=True)

        return {"message": f"File '{blob_name}' uploaded to container '{container_name}' successfully.", "filename": file.filename}
    
    except Exception as e:
        logging.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail="Upload failed, check logs for details.")

async def delete_file(file_id: str):
    tenant = "default"
    container_name = tenant.lower()
    container_client = get_or_create_container(container_name)
    blob_client = container_client.get_blob_client(file_id)
    try:
        await blob_client.delete_blob()
        return {"message": f"File '{file_id}' deleted successfully."}
    except Exception as e:
        logging.error(f"Delete error: {e}")
        raise HTTPException(status_code=500, detail="Delete failed, check logs for details.")
