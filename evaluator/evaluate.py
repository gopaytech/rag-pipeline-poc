import os
import sys
import pandas as pd
import ast

from llm import ModelGardenLLM
from langchain_ollama import OllamaLLM
from dotenv import load_dotenv
from ragas import evaluate, EvaluationDataset
from ragas.metrics import context_precision, context_recall

load_dotenv()

model = os.getenv('MODEL_GARDEN_MODEL')

llm_type = os.getenv('LLM_TYPE')
if llm_type == "model_garden":
    url = os.getenv('MODEL_GARDEN_URL')
    llm = ModelGardenLLM(api_url=url, model=model)
elif llm_type == "ollama":
    llm = OllamaLLM(model=model, temperature=0.4)
else:
    raise ValueError(f"Unsupported LLM type: {llm_type}")

df = pd.read_csv(sys.argv[1], usecols=['user_input', 'reference_contexts', 'reference'])
df['reference_contexts'] = df['reference_contexts'].apply(ast.literal_eval)
df['retrieved_contexts'] = df['reference_contexts']
dataset = EvaluationDataset.from_pandas(df)

if __name__ == "__main__":
    result = evaluate(dataset=dataset, metrics=[context_precision, context_recall], llm=llm)
    print(result)