# Retriever MCP Server

## Run Server

To run the Retriever MCP Server, use the following command:

```bash
go run ./cmd/retriever-mcp-server/main.go --json --debug --model-garden-url="" --model-name="" | jq -r .
```

## Run Client

To run the Retriever MCP Client, use the following command:

```bash
go run ./cmd/client/main.go --json --debug --query="why do we need barito?" --top-k=5 | jq -r .
```
