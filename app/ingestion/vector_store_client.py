import os
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()

class VectorStoreClient:
    def __init__(self, index_name: str = "tourwise", embedding_dim: int = 384):
        pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

        if not pc.has_index(index_name):
            pc.create_index(
                name=index_name,
                dimension=embedding_dim,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1"),
            )

        self.index = pc.Index(index_name)

    def upsert(self, items: list[dict], batch_size: int = 100):
        for i in tqdm(range(0, len(items), batch_size), desc="Upserting to Pinecone"):
            batch = [(item["id"], item["embedding"], item["metadata"]) for item in items[i:i+batch_size]]
            self.index.upsert(vectors=batch)

    def query(self, vector, top_k=5, filters=None):
        res = self.index.query(vector=vector, top_k=top_k, include_metadata=True, filter=filters)
        return res.matches
