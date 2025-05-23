import logging
import os
from typing import List
import openai
from openai import OpenAI
from pinecone import Pinecone, ServerlessSpec, CloudProvider, AwsRegion, VectorType
from fastapi import UploadFile, File
import httpx
logger = logging.getLogger(__name__)

pinecone_api_key = os.getenv("PINECONE_API_KEY")
pinecone_index_name = "gnosis"  # Replace with your index name

# Initialize Pinecone client
pc = Pinecone(api_key=pinecone_api_key)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def add_to_index(chunks: List[str], email: str):
    logger.info(f"Adding {len(chunks)} chunks to index for email: {email}")

    index = pc.Index(pinecone_index_name)
    namespace = email  # Use email as namespace

    vectors_to_upsert = []
    for i, chunk in enumerate(chunks):
        chunk_id = f"{email}-{i}"  # Unique ID for each chunk

        # 🔹 You MUST generate or fetch an embedding vector here
        embedding = await get_embedding(chunk)  # Or synchronous if not async

        vectors_to_upsert.append(
            (chunk_id, embedding, {"chunk_text": chunk})
        )

    index.upsert(
        vectors=vectors_to_upsert,
        namespace=namespace
    )

    logger.info(f"Successfully upserted {len(vectors_to_upsert)} vectors to index for email: {email}")

async def get_embedding(text: str) -> list[float]:
    async with httpx.AsyncClient() as client:
        res = await client.post(
            "https://api.openai.com/v1/embeddings",
            headers={
                "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
                "Content-Type": "application/json",
            },
            json={
                "model": "text-embedding-3-small",
                "input": text
            }
        )
        res.raise_for_status()
        data = res.json()
        return data["data"][0]["embedding"]


async def query_index_pinecone(query: str, email: str, top_k: int = 10):
    logger.info(f"Querying index for email: {email} with query: {query}")

    index = pc.Index(pinecone_index_name)
    namespace = email  # Use email as namespace

    #  Pinecone integrated embedding
    query_embedding = await get_embedding(query)
    results = index.query(
        top_k=top_k,
        namespace=namespace,
        vector=query_embedding,
        include_metadata=True
    )

    hits = results.get("matches", [])
    relevant_chunks = [hit.metadata["chunk_text"] for hit in hits]

    logger.info(f"Found {len(relevant_chunks)} relevant chunks for email: {email}")
    return relevant_chunks
