# POC RAG

- Create .env based on .env.example
```bash
source venv/bin/activate # if not exists create one by `uv venv`
cp .env.example .env # fill in the .env file with your settings
uv sync
```

## Generating Test Set
```bash
uv run generate_tests.py -o output_file.csv -c 10
```

## Evaluating Test Set
- Evaluate 
```bash
uv run evaluate.py test_dataset.csv
```
