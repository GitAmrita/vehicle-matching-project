import os, re
from qdrant_client import QdrantClient, models
from database.db import fetch_canonical_models
from data.noisy_data.noise import MAKE_ABBR_MAP
import uuid
from qdrant_client.http.models import PointStruct
from fastembed import TextEmbedding
import numpy as np

# --- 0) Config ---
QDRANT_URL = os.environ.get("QDRANT_URL", "https://0324670b-4e72-4a85-bdcb-05a3de9f8483.us-east4-0.gcp.cloud.qdrant.io:6333")      
QDRANT_API_KEY = os.environ.get("QDRANT_API_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.gxVecCFrpFoq8HXU2Kb9iRGQzkPXegNisG6zd25O8kA")
COLLECTION = "vehicles_semantic"
MODEL_NAME = "BAAI/bge-small-en-v1.5"

# --- 1) Connect to Qdrant Cloud ---
client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
    cloud_inference=False,  # Using local embeddings
)

# Initialize BAAI/bge-small-en-v1.5" model which comes out of the box with FastEmbed library (lightweight)
embedding_model = TextEmbedding(model_name=MODEL_NAME, max_length=512)

# Export for use in other modules
__all__ = ['client', 'embedding_model', 'COLLECTION', 'QDRANT_URL', 'QDRANT_API_KEY', 'MODEL_NAME']


def build_embeddings(limit: int = 1000, offset: int = 0, collection_name: str = COLLECTION) -> int:
    """
    Build and upload embeddings to Qdrant for a slice of canonical data.
    Uses FastEmbed for local text embeddings.

    Returns the number of points uploaded.
    """
    # Test basic connectivity first
    try:
        collections = client.get_collections()
        print(f"✅ Connected to Qdrant. Found {len(collections.collections)} collections.")
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        raise
    
    # Get the actual vector size from the model
    # BAAI/bge-small-en-v1.5 produces 384-dim vectors
    vec_size = 384
    
    # Ensure collection exists with correct vector size & distance
    client.recreate_collection(
        collection_name=collection_name,
        vectors_config=models.VectorParams(
            size=vec_size,
            distance=models.Distance.COSINE
        )
    )
    
    # Create indexes for filtering
    client.create_payload_index(
        collection_name=collection_name,
        field_name="year",
        field_schema=models.PayloadSchemaType.INTEGER
    )
    
    client.create_payload_index(
        collection_name=collection_name,
        field_name="make",
        field_schema=models.PayloadSchemaType.TEXT
    )
    
    client.create_payload_index(
        collection_name=collection_name,
        field_name="model",
        field_schema=models.PayloadSchemaType.TEXT
    )

    # Pull canonical data
    rows = fetch_canonical_models(limit=limit, offset=offset)
    print(f"Fetched {len(rows)} canonical models from offset {offset}")

    # Prepare data for embedding
    texts = []
    payloads = []
    ids = []
    
    for (make_name, model_name, year) in rows:
        text = f"{year} {make_name} {model_name}".strip().lower().replace("  ", " ") if model_name else f"{year} {make_name}".lower()
        abbr = MAKE_ABBR_MAP.get(make_name)
        alias_set = {make_name.lower()}
        if abbr:
            alias_set.add(str(abbr).lower())
        
        texts.append(text)
        payloads.append({
            "make": make_name,
            "model": model_name,
            "year": int(year),
            "normalized_text": text,
            "aliases": list(alias_set),
        })
        ids.append(uuid.uuid4().hex)

    print(f"Generating embeddings for {len(texts)} texts...")
    
    # Generate embeddings using FastEmbed
    embeddings = list(embedding_model.embed(texts))
    
    # Convert to numpy arrays and normalize
    embeddings = np.array(embeddings)
    
    # Create points for Qdrant
    points = []
    for i, (embedding, payload, point_id) in enumerate(zip(embeddings, payloads, ids)):
        point = PointStruct(
            id=point_id,
            payload=payload,
            vector=embedding.tolist()  # Convert to list for JSON serialization
        )
        points.append(point)

    print(f"Uploading {len(points)} points to Qdrant...")
    client.upload_points(
        collection_name=collection_name, 
        points=points, 
        batch_size=128
    )
    
    print(f"✅ Successfully uploaded {len(points)} points!")
    return len(points)

