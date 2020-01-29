package main

import "flag"

var (
	// commandline flags
	flagAttackList            = flag.String("attacks", "", "attack list CSV")
	flagInput                 = flag.String("in", ".", "input directory (default is current directory)")
	flagOut                   = flag.String("out", ".", "output path")
	flagNumWorkers            = flag.Int("workers", 100, "number of parallel processed files")
	flagMaxFiles              = flag.Int("max", 0, "max number of processed files")
	flagDebug                 = flag.Bool("debug", false, "toggle debug mode")
	flagReuseLineBuffer       = flag.Bool("reuse", false, "reuse CSV line buffer")
	flagSkipIncompleteRecords = flag.Bool("skip-incomplete", false, "skip lines that contain empty values")
	flagZeroIncompleteRecords = flag.Bool("zero-incomplete", true, "skip lines that contain empty values")
	flagCountAttacks          = flag.Bool("count-attacks", false, "count attacks")
)
