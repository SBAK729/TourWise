import os
import json
import yaml
import hashlib
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

# Load dataset
with open(dataset_path, "r") as f:
    data = json.load(f)

def build_full_text(doc):
    """Construct a text representation of the document including all relevant fields."""
    text_parts = [
        f"Name: {doc.get('name','')}",
        f"Category: {doc.get('category','')}",
        f"Description: {doc.get('description','')}",
        f"Location: {doc.get('location','')}",
        f"Tags: {', '.join(doc.get('tags', []))}" if doc.get('tags') else "",
        f"Estimated total cost USD: {doc.get('estimated_total_cost_usd','')}",
        f"Recommended duration days: {doc.get('recommended_duration_days','')}",
    ]

    # Include nearby hotels
    hotels = doc.get("nearby_hotels", [])
    if hotels:
        hotel_text = "Nearby hotels: " + ", ".join(
            [f"{h['name']} (avg cost per night: {h.get('avg_cost_per_night_usd','N/A')})" for h in hotels]
        )
        text_parts.append(hotel_text)

    # Include nearby restaurants
    restaurants = doc.get("nearby_restaurants", [])
    if restaurants:
        restaurant_text = "Nearby restaurants: " + ", ".join(
            [f"{r['name']} (avg meal cost: {r.get('avg_meal_cost_usd','N/A')})" for r in restaurants]
        )
        text_parts.append(restaurant_text)

    return ". ".join(filter(None, text_parts))


all_items = []
for doc in tqdm(data, desc="Processing documents"):
    doc_id = hashlib.md5(doc["name"].encode()).hexdigest()
    base_text = build_full_text(doc)
    chunks = chunk_text(base_text, chunk_size, overlap)

    # Create upsert items
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
