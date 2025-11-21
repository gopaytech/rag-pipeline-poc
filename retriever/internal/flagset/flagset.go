package flagset

import "flag"

type Flag struct {
	_           struct{}
	addrFlag    string
	debugFlag   bool
	jsonFlag    bool
	versionFlag bool
}

func (f *Flag) Addr() string {
	return f.addrFlag
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

func ParseFlag(args []string) (*Flag, error) {
	f := &Flag{}
	fs := flag.NewFlagSet(args[0], flag.ExitOnError)
	fs.StringVar(&f.addrFlag, "addr", ":1428", "mcp server address")
	fs.BoolVar(&f.debugFlag, "debug", false, "enable debug logging")
	fs.BoolVar(&f.jsonFlag, "json", false, "enable JSON logging")
	fs.BoolVar(&f.versionFlag, "version", false, "print version and exit")

	return f, fs.Parse(args[1:])
}
