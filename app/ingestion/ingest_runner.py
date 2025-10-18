import os, json, yaml, hashlib
from tqdm import tqdm
from datetime import datetime
from app.core.config import settings  
from app.ingestion.embeddings_client import EmbeddingsClient
from app.ingestion.vector_store_client import VectorStoreClient
from app.ingestion.utils_text import chunk_text

# Load config
with open("app/ingestion/ingest_config.yml") as f:
    cfg = yaml.safe_load(f)

dataset_path = cfg["dataset_path"]
chunk_size = cfg["chunk_size"]
overlap = cfg["chunk_overlap"]
model_name = cfg["embedding_model"]
index_name = cfg["pinecone_index_name"]

# Initialize clients
embedder = EmbeddingsClient(model_name)
vector_client = VectorStoreClient(index_name)

with open(dataset_path, "r") as f:
    data = json.load(f)

all_items = []
for doc in tqdm(data, desc="Processing documents"):
    doc_id = hashlib.md5(doc["name"].encode()).hexdigest()
    base_text = f"{doc['name']}. {doc.get('description', '')}"
    # text = clean_text(base_text)
    chunks = chunk_text(base_text, chunk_size, overlap)

   # When creating upsert items
    for i, chunk in enumerate(chunks):
        item = {
            "id": f"{doc_id}_{i}",
            "embedding": None,
            "metadata": {
                "doc_id": doc_id,
                "chunk_id": i,
                "name": doc.get("name"),
                "category": doc.get("category"),
                "location": doc.get("location"),
                "distance_from_addis_km": doc.get("distance_from_addis_km"),
                "tags": doc.get("tags", []),
                "text": chunk,  
                "source": "ethiopia_tourism_dataset_50plus"
            }
        }
        all_items.append(item)


# Embed & upsert in batches
texts = [x["metadata"]["text"] for x in all_items]
embeddings = embedder.embed_texts(texts)
for i, emb in enumerate(embeddings):
    all_items[i]["embedding"] = emb


vector_client.upsert(all_items)
print(f"Ingestion complete: {len(all_items)} chunks uploaded.")
