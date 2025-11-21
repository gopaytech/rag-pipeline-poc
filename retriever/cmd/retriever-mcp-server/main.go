package main

import (
	"context"
	"errors"
	"log/slog"
	"net/http"
	"os"
	"os/signal"
	"syscall"

	"github.com/gopaytech/rag-pipeline-poc/retriever/internal/flagset"
	"github.com/gopaytech/rag-pipeline-poc/retriever/internal/tools"
	"github.com/modelcontextprotocol/go-sdk/mcp"
)

var (
	BuildTime = "unknown"
	Name      = "retriever-mcp-server"
	Version   = "dev"
)

func initializeLogger(debug, json bool) {
	var opts slog.HandlerOptions
	if debug {
		opts.Level = slog.LevelDebug
	} else {
		opts.Level = slog.LevelInfo
	}
	var handler slog.Handler
	if json {
		handler = slog.NewJSONHandler(os.Stdout, &opts)
	} else {
		handler = slog.NewTextHandler(os.Stdout, &opts)
	}
	slog.SetDefault(slog.New(handler))
}

func run(ctx context.Context, args []string) error {
	flag, err := flagset.ParseFlag(args[:])
	if err != nil {
		return err
	}

	initializeLogger(flag.Debug(), flag.JSON())

	if flag.Version() {
		slog.LogAttrs(ctx,
			slog.LevelInfo,
			"version info",
			slog.String("name", Name),
			slog.String("version", Version),
			slog.String("build_time", BuildTime),
		)
		return nil
	}

	slog.LogAttrs(ctx,
		slog.LevelInfo,
		"starting server",
		slog.String("name", Name),
		slog.String("version", Version),
		slog.String("build_time", BuildTime),
		slog.String("addr", flag.Addr()),
	)

	server := mcp.NewServer(&mcp.Implementation{
		Name:    Name,
		Version: Version,
	}, &mcp.ServerOptions{
		Logger: slog.Default().WithGroup("mcp_server"),
	})
	mcp.AddTool(server, tools.QueryTool, tools.QueryFunc)

	errCh := make(chan error, 1)
	go func() {
		if err := http.ListenAndServe(flag.Addr(),
			mcp.NewStreamableHTTPHandler(func(r *http.Request) *mcp.Server {
				return server
			}, &mcp.StreamableHTTPOptions{
				Logger: slog.Default().WithGroup("mcp_http"),
			}),
		); err != nil && !errors.Is(err, http.ErrServerClosed) {
			slog.LogAttrs(ctx,
				slog.LevelError,
				"failed to start http server",
				slog.String("error", err.Error()),
			)
			errCh <- err
		}
	}()

	select {
	case <-ctx.Done():
		slog.LogAttrs(ctx,
			slog.LevelInfo,
			"shutting down server",
		)
		return nil
	case err := <-errCh:
		return err
	}
}

func main() {
	ctx, cancel := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM, syscall.SIGINT)
	defer cancel()

	if err := run(ctx, os.Args[:]); err != nil {
		slog.Default().LogAttrs(ctx,
			slog.LevelError,
			"run failed",
			slog.String("error", err.Error()),
		)
		os.Exit(1)
	}
}
