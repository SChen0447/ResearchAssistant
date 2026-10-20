import os
os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")
from langchain_core.embeddings import Embeddings
from langchain_huggingface import HuggingFaceEmbeddings
from typing import List


class BGEEmbeddings(Embeddings):
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.embeddings = HuggingFaceEmbeddings(
            model_name=model_name,
            encode_kwargs={"batch_size": 32}
        )

    def embed_documents(self, documents: List[str]) -> List[List[float]]:
        return self.embeddings.embed_documents(documents)

    def embed_query(self, query: str) -> List[float]:
        return self.embeddings.embed_query(query)
