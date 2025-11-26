import argparse
from dotenv import load_dotenv
from langchain_community.document_loaders import FileSystemBlobLoader
from langchain_community.document_loaders.generic import GenericLoader
from langchain_community.document_loaders.parsers import PyPDFParser
from langchain_core.documents import Document
from pandas import DataFrame 
from ragas.testset import TestsetGenerator
from llm import load_llm
from embeddings import load_embeddings

load_dotenv()

def load_docs(path: str) -> list[Document]:
    loader = GenericLoader(
        blob_loader=FileSystemBlobLoader(
            path=path,
            glob="**/*.pdf",
        ),
        blob_parser=PyPDFParser(),
    )
    return loader.load()

def generate_dataset(docs: list[Document], count: int) -> DataFrame:
    llm = load_llm()
    embeds = load_embeddings()

    generator = TestsetGenerator(llm=llm, embedding_model=embeds)
    dataset = generator.generate_with_langchain_docs(docs, testset_size=count)
    df = dataset.to_pandas()
    return df[['user_input', 'reference_contexts', 'reference']]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output', required=True, type=str)
    parser.add_argument('-c', '--count', required=True, type=int)
    args = parser.parse_args()
    
    docs = load_docs("../datasets")
    df = generate_dataset(docs, args.count)
    df.to_csv(args.output, index=False)

if __name__ == "__main__":
    main()
