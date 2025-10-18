import os
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv
import os

from tqdm import tqdm


load_dotenv()
class VectorStoreClient:
    def __init__(self, index_name: str = "tourwise"):
        pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

        if not pc.has_index(index_name):
            pc.create_index(
                name=index_name,
                dimension=384,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1"),
            )

        self.index = pc.Index(index_name)


    def upsert(self, items: list[dict]):
        batch = []
        for item in tqdm(items, desc="Upserting to Pinecone"):
            vector = (item["id"], item["embedding"], item["metadata"])
            batch.append(vector)
            if len(batch) >= 100:
                self.index.upsert(vectors=batch)
                batch = []
        if batch:
            self.index.upsert(vectors=batch)

    def query(self, vector, top_k=5, filters=None):
        res = self.index.query(vector=vector, top_k=top_k, include_metadata=True, filter=filters)
        return res.matches
