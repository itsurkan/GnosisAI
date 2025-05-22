from pinecone import (
    Pinecone,
    ServerlessSpec,
    CloudProvider,
    AwsRegion,
    VectorType
)
import os
from fastapi import FastAPI, UploadFile, File, Header, HTTPException, APIRouter
from app.azure_storage import upload_file
from starlette.middleware.sessions import SessionMiddleware
import os
from fastapi.middleware.cors import CORSMiddleware
from authlib.jose import jwt
from app.tokenDecoder import decode_jwt_payload
from app.emailToTenant import email_to_tenant
from app.pinecone import add_to_index
import logging
logger = logging.getLogger(__name__)


pineconeKey=os.getenv("SESSION_SECRET_KEY")
# 1. Instantiate the Pinecone client
pc = Pinecone(api_key=pineconeKey)


async def add_to_index(file: UploadFile = File(...), email: str = None):
    logging.info("Start upload file")
   

# # 2. Create an index
# index_config = pc.create_index(
#     name="index-name",
#     dimension=1536,
#     spec=ServerlessSpec(
#         cloud=CloudProvider.AWS,
#         region=AwsRegion.US_EAST_1
#     ),
#     vector_type=VectorType.DENSE
# )

# # 3. Instantiate an Index client
# idx = pc.Index()

# # 4. Upsert embeddings
# idx.upsert(
#     vectors=[
#         ("id1", [0.1, 0.2, 0.3, 0.4, ...], {"metadata_key": "value1"}),
#         ("id2", [0.2, 0.3, 0.4, 0.5, ...], {"metadata_key": "value2"}),
#     ],
#     namespace="example-namespace"
# )

# # 5. Query your index using an embedding
# query_embedding = [...] # list should have length == index dimension
# idx.query(
#     vector=query_embedding,
#     top_k=10,
#     include_metadata=True,
#     filter={"metadata_key": { "$eq": "value1" }}
# )