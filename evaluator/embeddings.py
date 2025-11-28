import os
import requests
from typing import List
from langchain_core.embeddings import Embeddings
from langchain_ollama import OllamaEmbeddings
from deepeval.models import DeepEvalBaseEmbeddingModel

class OllamaRagasEmbeddings(OllamaEmbeddings):
    # need to implement BaseRagasEmbeddings https://docs.ragas.io/en/stable/references/embeddings/

    def __init__(self, model: str):
        super().__init__(model=model)

    async def embed_text(self, text: str, **kwargs) -> List[float]:
        return self.aembed_query(text)

    async def aembed_text(self, text: str, **kwargs) -> List[float]:
        return self.aembed_query(text)
    
class DeepEvalEmbeddings(DeepEvalBaseEmbeddingModel):
    api_url: str
    model: str

    def __init__(self, api_url, model):
        self.api_url = api_url
        self.model = model

    def load_model(self):
        return self

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        response = requests.post(
            self.api_url,
            headers = {"Content-Type": "application/json"},
            json = {
                "model": self.model,
                "input": texts,
                "encoding_format": "float",
            },
        )
        response.raise_for_status()

        result = response.json()
        embeddings = [item['embedding'] for item in result['data']]

        return embeddings

    def embed_text(self, text: str) -> List[float]:
        return self.a_embed_texts([text])[0]

    async def a_embed_text(self, text: str) -> List[float]:
        return self.embed_text(text)
    
    async def a_embed_texts(self, texts: List[str]) -> List[List[float]]:
        return self.embed_texts(texts)

    def get_model_name(self):
        self.model

class LangChainEmbeddings(Embeddings):
    api_url: str
    model: str

    def __init__(self, api_url, model, **kwargs):
        super().__init__(**kwargs)
        self.api_url = api_url
        self.model = model

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        response = requests.post(
            self.api_url,
            headers = {"Content-Type": "application/json"},
            json = {
                "model": self.model,
                "input": texts,
                "encoding_format": "float",
            },
        )
        response.raise_for_status()

        result = response.json()
        embeddings = [item['embedding'] for item in result['data']]

        return embeddings

    def embed_query(self, text: str) -> List[float]:
        return self.embed_documents([text])[0]
    
    async def embed_text(self, text: str):
        return self.embed_query(text)

def load_embeddings():
    llm_type = os.getenv('LLM_TYPE')
    embedding = os.getenv('EMBEDDING_MODEL')
    if llm_type == "model_garden":
        embed_url = os.getenv('EMBEDDING_URL')
        return LangChainEmbeddings(api_url=embed_url, model=embedding)
    elif llm_type == "ollama":
        return OllamaRagasEmbeddings(model=embedding)
    raise ValueError(f"Unsupported LLM type: {llm_type}")
