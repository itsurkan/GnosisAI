from fastapi import UploadFile, File, HTTPException
from azure.storage.blob import BlobServiceClient, ContainerClient
import os
import logging
import uuid
import asyncio
import logging
from app.emailToTenant import email_to_tenant

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

async def upload_file(file: UploadFile = File(...), email: str = None):
    logging.info("Start upload file")
    container_name = email_to_tenant(email)
    # Перевірка валідності імені контейнера
    if not container_name.replace('-', '').isalnum():
        raise HTTPException(status_code=400, detail="Invalid tenant/container name")

    try:
        container_client = get_or_create_container(container_name)
        blob_name = str(uuid.uuid4()) + "_" + file.filename
        blob_client = container_client.get_blob_client(blob_name)

        content = await file.read()
        metadata = {"filename": file.filename}
        blob_client.upload_blob(content, overwrite=True, metadata=metadata)

        logger.info(f"Uploaded file '{blob_name}' to container '{container_name}'.")
        return {"message": f"File '{blob_name}' uploaded successfully."}
    except Exception as e:
        logger.error(f"Upload error for file '{file.filename}': {e}")
        raise

async def delete_file(file_id: str, email: str = None):
    try:
        tenant = email_to_tenant(email)
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

async def list_files(email: str):
    container_name = email_to_tenant(email)
    container_client = get_or_create_container(container_name)
    file_names = []
    blobs = container_client.list_blobs()
    for blob in blobs:
        file_name = blob.name.split("_", 1)[1] if "_" in blob.name else blob.name
        blob_properties = container_client.get_blob_client(blob.name).get_blob_properties()
        file_type = blob_properties.content_settings.content_type
        file_size = blob_properties.size
        file_names.append({"fullname": blob.name, "name": file_name, "file_type": file_type, "file_size": file_size})
    return file_names
