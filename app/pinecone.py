import logging
import os
from typing import List

from pinecone import Pinecone, ServerlessSpec, CloudProvider, AwsRegion, VectorType
from fastapi import UploadFile, File

logger = logging.getLogger(__name__)

pinecone_api_key = os.getenv("PINECONE_API_KEY")
pinecone_index_name = "gnosis"  # Replace with your index name

# Initialize Pinecone client
pc = Pinecone(api_key=pinecone_api_key)

# Check if index exists, create if it doesn't
if pinecone_index_name not in pc.list_indexes():
    pc.create_index(
        name=pinecone_index_name,
        dimension=1536,  # Standard dimension for many embedding models
        spec=ServerlessSpec(
            cloud=CloudProvider.AWS,
            region=AwsRegion.US_EAST_1
        ),
        vector_type=VectorType.DENSE
    )


async def add_to_index(chunks: List[str], email: str):
    logger.info(f"Adding {len(chunks)} chunks to index for email: {email}")

    index = pc.Index(pinecone_index_name)
    namespace = email  # Use email as namespace

    vectors_to_upsert = []
    for i, chunk in enumerate(chunks):
        chunk_id = f"{email}-{i}"  # Unique ID for each chunk
        #  Pinecone integrated embedding
        vectors_to_upsert.append(
            (chunk_id, [], {"chunk_text": chunk})
        )

    index.upsert(
        vectors=vectors_to_upsert,
        namespace=namespace
    )

    logger.info(f"Successfully upserted {len(vectors_to_upsert)} vectors to index for email: {email}")


async def query_index(query: str, email: str, top_k: int = 10):
    logger.info(f"Querying index for email: {email} with query: {query}")

    index = pc.Index(pinecone_index_name)
    namespace = email  # Use email as namespace

    #  Pinecone integrated embedding
    results = index.query(
        top_k=top_k,
        namespace=namespace,
        query={
            "inputs": {
                "text": query
            }
        },
        include_metadata=True
    )

    hits = results.get("matches", [])
    relevant_chunks = [hit.metadata["chunk_text"] for hit in hits]

    logger.info(f"Found {len(relevant_chunks)} relevant chunks for email: {email}")
    return relevant_chunks
