package tools

import (
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"log/slog"

	"github.com/gopaytech/rag-pipeline-poc/retriever/internal/model_garden"
	"github.com/milvus-io/milvus/client/v2/entity"
	"github.com/milvus-io/milvus/client/v2/index"
	"github.com/milvus-io/milvus/client/v2/milvusclient"
	"github.com/modelcontextprotocol/go-sdk/mcp"
)

type Tools struct {
	_           struct{}
	database    *milvusclient.Client
	logger      *slog.Logger
	modelGarden *model_garden.ModelGarden
}

func RegisterTools(logger *slog.Logger, server *mcp.Server, database *milvusclient.Client, modelGarden *model_garden.ModelGarden) *Tools {
	t := &Tools{
		database:    database,
		logger:      logger.WithGroup("tools"),
		modelGarden: modelGarden,
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

	if ok, err := t.database.HasCollection(ctx, milvusclient.NewHasCollectionOption("pdf_collection")); err != nil {
		return nil, nil, err
	} else if !ok {
		return nil, nil, errors.New("collection does not exist")
	}

	denseVector := make([]entity.Vector, 0, 1)
	if resp, err := t.modelGarden.Vectorize(ctx, []string{input.Query}); err != nil {
		return nil, nil, err
	} else {
		denseVector = append(denseVector, entity.FloatVector(resp[0]))
	}

	// https://github.com/milvus-io/milvus/issues/45235
	param := index.NewSparseAnnParam()
	param.WithDropRatio(0.2)

	rs, err := t.database.HybridSearch(ctx,
		milvusclient.NewHybridSearchOption(
			"pdf_collection",
			input.TopK,
			// vector search
			milvusclient.NewAnnRequest(
				"vector_dense",
				input.TopK,
				denseVector...,
			).WithANNSField("vector_dense"),
			// full-text search
			milvusclient.NewAnnRequest(
				"vector_sparse",
				input.TopK,
				entity.Text(input.Query),
			).
				WithANNSField("vector_sparse").
				WithAnnParam(param).
				WithSearchParam("metric_type", "BM25").
				WithSearchParam("index_type", string(index.SparseInverted)),
		).
			WithOutputFields("text", "metadata").
			WithReranker(milvusclient.NewRRFReranker()),
	)
	if err != nil {
		return nil, nil, err
	}

	if len(rs) == 0 || rs[0].ResultCount == 0 {
		return nil, &QueryOutput{
			TopK: []QueryResult{},
		}, nil
	}

	topk := make([]QueryResult, 0, rs[0].ResultCount)

	r := rs[0]
	for i := 0; i < r.ResultCount; i++ {
		var qr QueryResult
		qr.Score = float64(r.Scores[i])
		qr.Text = r.GetColumn("text").FieldData().GetScalars().GetStringData().GetData()[i]
		if err := json.NewDecoder(bytes.NewReader(
			r.GetColumn("metadata").FieldData().GetScalars().GetJsonData().GetData()[i],
		)).Decode(&qr.Metadata); err != nil {
			return nil, nil, err
		}
		topk = append(topk, qr)
	}
	return nil, &QueryOutput{
		TopK: topk,
	}, nil
}
