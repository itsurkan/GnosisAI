from fastapi import UploadFile, File, HTTPException
from azure.storage.blob import BlobServiceClient, ContainerClient
import os
import logging
import uuid
import asyncio
import logging

logger = logging.getLogger(__name__)


AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)

def get_or_create_container(container_name: str) -> ContainerClient:
    try:
        container_client = blob_service_client.get_container_client(container_name)
        if not container_client.exists():
            container_client.create_container()
            logger.info(f"Container '{container_name}' created.")
        else:
            logger.info(f"Container '{container_name}' already exists.")
        return container_client
    except Exception as e:
        logger.error(f"Error in get_or_create_container('{container_name}'): {e}")
        raise

async def upload_file(file: UploadFile = File(...)):
    logging.info("Start upload file")
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

        logger.info(f"Uploaded file '{blob_name}' to container '{container_name}'.")
        return {"message": f"File '{blob_name}' uploaded successfully."}
    except Exception as e:
        logger.error(f"Upload error for file '{file.filename}': {e}")
        raise

async def delete_file(file_id: str):
    try:
        tenant = "default"
        container_name = tenant.lower()
        container_client = get_or_create_container(container_name)
        blob_client = container_client.get_blob_client(file_id)
        logging.info("Root endpoint hit")
        exists = await asyncio.to_thread(blob_client.exists)
        if not exists:
            logger.warning(f"File '{file_id}' not found in container '{container_name}'.")
            raise HTTPException(status_code=404, detail="File not found.")

        await asyncio.to_thread(blob_client.delete_blob)

        logger.info(f"Deleted file '{file_id}' from container '{container_name}'.")
        return {"message": f"File '{file_id}' deleted successfully."}

    except HTTPException as http_exc:
        raise http_exc

    except Exception as e:
        logger.error(f"Delete error for file '{file_id}': {e}")
        raise HTTPException(status_code=500, detail="Delete failed, check logs for details.")