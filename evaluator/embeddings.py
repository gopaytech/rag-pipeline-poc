import requests
from typing import List
from langchain_core.embeddings import Embeddings

class ModelGardenEmbeddings(Embeddings):
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
