package tools

import (
	"context"
	"errors"
	"log/slog"

	milvus "github.com/milvus-io/milvus-sdk-go/v2/client"
	"github.com/milvus-io/milvus-sdk-go/v2/entity"
	"github.com/modelcontextprotocol/go-sdk/mcp"
)

type Tools struct {
	_        struct{}
	database milvus.Client
	logger   *slog.Logger
}

func RegisterTools(logger *slog.Logger, server *mcp.Server, database milvus.Client) *Tools {
	t := &Tools{
		database: database,
		logger:   logger.WithGroup("tools"),
	}

	mcp.AddTool(server, QueryTool, t.Query)

	return t
}

func (t *Tools) Query(ctx context.Context,
	req *mcp.CallToolRequest,
	input QueryInput,
) (*mcp.CallToolResult, *QueryOutput, error) {
	t.logger.LogAttrs(ctx,
		slog.LevelInfo,
		"received query tool request",
		slog.String("query", input.Query),
		slog.Any("req", req),
	)

	sp, err := entity.NewIndexBinFlatSearchParam(10) // default search params
	if err != nil {
		return nil, nil, err
	}

	if ok, err := t.database.HasCollection(ctx, "pdf_collection"); err != nil {
		return nil, nil, err
	} else if !ok {
		return nil, nil, errors.New("collection does not exist")
	}

	result, err := t.database.Search(ctx,
		"pdf_collection",
		[]string{},
		"",
		[]string{"text", "metadata"},
		nil,
		"data",    // vector field
		entity.L2, // default metric type
		5,         // top k
		sp,
		[]milvus.SearchQueryOptionFunc{}...,
	)
	if err != nil {
		return nil, nil, err
	}
	t.logger.LogAttrs(ctx,
		slog.LevelInfo,
		"search results",
		slog.Any("result", result),
	)

	// another optional to do is augment the input query
	return nil, &QueryOutput{
		TopK: []string{"result1", "result2", "result3"},
	}, nil
}
