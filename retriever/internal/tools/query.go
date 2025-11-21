package tools

import (
	"context"

	"github.com/modelcontextprotocol/go-sdk/mcp"
)

var (
	QueryTool = &mcp.Tool{
		Name:        "query",
		Description: "Query the vector database with a text query and return the top k results.",
	}
)

type (
	QueryInput struct {
		_     struct{}
		Query string `json:"query" jsonschema:"the query that will be vectorized and searched against the vector database"`
	}
	QueryOutput struct {
		_    struct{}
		TopK []string `json:"top_k" jsonschema:"the top k results from the vector database search"`
	}
)

func QueryFunc(ctx context.Context, req *mcp.CallToolRequest, input QueryInput) (*mcp.CallToolResult, *QueryOutput, error) {
	return nil, &QueryOutput{
		TopK: []string{"result1", "result2", "result3"},
	}, nil
}
