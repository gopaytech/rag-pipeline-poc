import argparse
import os
import sys
import pandas as pd
import ast

from dotenv import load_dotenv
from ragas import evaluate, EvaluationDataset
from ragas.metrics import context_precision, context_recall
from llm import load_llm

load_dotenv()

llm = load_llm()

def load_dataset(path: str) -> EvaluationDataset:
    df = pd.read_csv(path, usecols=['user_input', 'reference_contexts', 'reference'])
    df['reference_contexts'] = df['reference_contexts'].apply(ast.literal_eval)
    df['retrieved_contexts'] = df['reference_contexts']
    return EvaluationDataset.from_pandas(df)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('file_path', type=str)
    args = parser.parse_args()
    
    dataset = load_dataset(args.file_path)
    result = evaluate(dataset=dataset, metrics=[context_precision, context_recall], llm=llm)
    print(result)

if __name__ == "__main__":
    main()