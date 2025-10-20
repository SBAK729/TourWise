from sentence_transformers import SentenceTransformer
import numpy as np

class EmbeddingsClient:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def embed_texts(self, texts: list[str], batch_size: int = 32) -> list[list[float]]:
        return self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=True,
            convert_to_numpy=True
        ).tolist()

    def embed_query(self, query: str) -> list[float]:
        return self.model.encode([query], convert_to_numpy=True)[0].tolist()
