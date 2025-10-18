from sentence_transformers import SentenceTransformer
import numpy as np

class EmbeddingsClient:
    def __init__(self, model_name: str):
        self.model = SentenceTransformer(model_name)

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return self.model.encode(texts, show_progress_bar=True, convert_to_numpy=True).tolist()

    def embed_query(self, query: str) -> list[float]:
        return self.model.encode([query], convert_to_numpy=True)[0].tolist()
