import requests
import os

from typing import List
from langchain_core.language_models.llms import LLM
from langchain_core.outputs.llm_result import LLMResult, Generation
from langchain_ollama import OllamaLLM
from deepeval.models import DeepEvalBaseLLM

class DeepEvalModel(DeepEvalBaseLLM):
    api_url: str
    model: str
    temperature: float = 0.4

    def __init__(self, api_url, model):
        self.api_url = api_url
        self.model = model

    def load_model(self):
        return self

    def generate(self, prompt: str) -> str:
        response = requests.post(
            self.api_url,
            headers = {"Content-Type": "application/json"},
            json = {
                "model": self.model,
                "messages": [{
                    "role": "user", 
                    "content": [
                        {
                            "type": "text",
                            "text": prompt,
                        }
                    ]
                }],
                "temperature": self.temperature
            }
        )

        response.raise_for_status()

        output = response.json()["choices"][0]["message"]["content"]

        start_token = "```json"
        if start_token in output:
            output = output.split(start_token, 1)[-1]
            output = output.split("```")[0].strip()

        return output

    async def a_generate(self, prompt: str) -> str:
        return self.generate(prompt)

    def get_model_name(self):
        return self.model

class LangChainModel(LLM):
    api_url: str
    model: str
    temperature: float = 0.4
    
    @property
    def _llm_type(self):
        return "model_garden"

    def _call(self, prompt: str, run_manager=None, stop=None):
        response = requests.post(
            self.api_url,
            headers = {"Content-Type": "application/json"},
            json = {
                "model": self.model,
                "messages": [{
                    "role": "user", 
                    "content": [
                        {
                            "type": "text",
                            "text": prompt,
                        }
                    ]
                }],
                "temperature": self.temperature
            }
        )

        response.raise_for_status()

        output = response.json()["choices"][0]["message"]["content"]

        start_token = "```json"
        if start_token in output:
            output = output.split(start_token, 1)[-1]
            output = output.split("```")[0].strip()

        return output

    def generate(self, prompts: List[str], **kwargs):
        generations = []
        for prompt in prompts:
            text = self._call(prompt)
            generations.append([Generation(text=text)])
        return LLMResult(generations=generations)

def load_llm():
    llm_type = os.getenv('LLM_TYPE')
    model = os.getenv('MODEL_GARDEN_MODEL')
    if llm_type == "model_garden":
        url = os.getenv('MODEL_GARDEN_URL')
        return LangChainModel(api_url=url, model=model)
    elif llm_type == "ollama":
        return OllamaLLM(model=model, temperature=0.4)
    raise ValueError(f"Unsupported LLM type: {llm_type}")
