package flagset

import (
	"flag"
	"log/slog"
	"os"
)

type ServerFlag struct {
	Flag
	addrFlag       string
	milvusAddr     string
	modelGardenURL string
	modelName      string
}

func (s *ServerFlag) Addr() string {
	return s.addrFlag
}
func (s *ServerFlag) MilvusAddr() string {
	return s.milvusAddr
}

func (s *ServerFlag) ModelGardenURL() string {
	return s.modelGardenURL
}

func (s *ServerFlag) ModelName() string {
	return s.modelName
}

type ClientFlag struct {
	Flag
	serverAddr string
	query      string
	topk       int
}

func (c *ClientFlag) ServerAddr() string {
	return c.serverAddr
}

func (c *ClientFlag) Query() string {
	return c.query
}

func (c *ClientFlag) TopK() int {
	return c.topk
}

type Flag struct {
	_           struct{}
	debugFlag   bool
	jsonFlag    bool
	versionFlag bool
}

func (f *Flag) Debug() bool {
	return f.debugFlag
}

func (f *Flag) JSON() bool {
	return f.jsonFlag
}

func (f *Flag) Version() bool {
	return f.versionFlag
}

func ParseClientFlag(args []string) (*ClientFlag, error) {
	f := &ClientFlag{}
	fs := flag.NewFlagSet(args[0], flag.ExitOnError)
	fs.StringVar(&f.serverAddr, "server-addr", "http://localhost:1428", "mcp server address")
	fs.StringVar(&f.query, "query", "", "the query string to search")
	fs.IntVar(&f.topk, "top-k", 5, "the number of top results to return")
	fs.BoolVar(&f.debugFlag, "debug", false, "enable debug logging")
	fs.BoolVar(&f.jsonFlag, "json", false, "enable JSON logging")
	fs.BoolVar(&f.versionFlag, "version", false, "print version and exit")

	err := fs.Parse(args[1:])
	if err != nil {
		return nil, err
	}
	f.initializeLogger()

	return f, nil
}

func ParseServerFlag(args []string) (*ServerFlag, error) {
	f := &ServerFlag{}
	fs := flag.NewFlagSet(args[0], flag.ExitOnError)
	fs.StringVar(&f.addrFlag, "addr", ":1428", "mcp server address")
	fs.BoolVar(&f.debugFlag, "debug", false, "enable debug logging")
	fs.BoolVar(&f.jsonFlag, "json", false, "enable JSON logging")
	fs.StringVar(&f.milvusAddr, "milvus-addr", "localhost:19530", "milvus vector database address")
	fs.StringVar(&f.modelGardenURL, "model-garden-url", "https://modelgarden.com/embeddings", "Model Garden embeddings endpoint URL")
	fs.StringVar(&f.modelName, "model-name", "embeddinggemma-300m", "Model Garden model name for embeddings")
	fs.BoolVar(&f.versionFlag, "version", false, "print version and exit")

	err := fs.Parse(args[1:])
	if err != nil {
		return nil, err
	}
	f.initializeLogger()

	return f, nil
}

func (f *Flag) initializeLogger() {
	var opts slog.HandlerOptions
	if f.Debug() {
		opts.Level = slog.LevelDebug
	} else {
		opts.Level = slog.LevelInfo
	}
	var handler slog.Handler
	if f.JSON() {
		handler = slog.NewJSONHandler(os.Stdout, &opts)
	} else {
		handler = slog.NewTextHandler(os.Stdout, &opts)
	}
	slog.SetDefault(slog.New(handler))
}
