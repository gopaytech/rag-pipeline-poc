import requests
from langchain_core.language_models.llms import LLM
from langchain_core.outputs.llm_result import LLMResult, Generation
from typing import List

class ModelGardenLLM(LLM):
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
