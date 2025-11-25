package tools

import (
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
		TopK  int    `json:"top_k" jsonschema:"the number of top results to return from the vector database search"`
	}
	QueryResult struct {
		Text     string         `json:"text" jsonschema:"the text content of the result"`
		Score    float64        `json:"score" jsonschema:"the similarity score of the result"`
		Metadata map[string]any `json:"metadata" jsonschema:"the metadata of the result"`
	}
	QueryOutput struct {
		_    struct{}
		TopK []QueryResult `json:"top_k" jsonschema:"the top k results from the vector database search"`
	}
)
