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
	flagReuseLineBuffer       = flag.Bool("reuse", true, "reuse CSV line buffer")
	flagSkipIncompleteRecords = flag.Bool("skip-incomplete", false, "skip lines that contain empty values")
	flagZeroIncompleteRecords = flag.Bool("zero-incomplete", true, "skip lines that contain empty values")
	flagCountAttacks          = flag.Bool("count-attacks", false, "count attacks")
	flagColumnSummaries       = flag.String("colsums", "", "column summary JSON file for loading")
	flagAnalyzeOnly           = flag.Bool("analyze-only", false, "analyze only")
	flagPathSuffix            = flag.String("suffix", "_sorted.csv", "suffix for all csv files to be parsed")
	flagOffset                = flag.Int("offset", 0, "index offset from which file to start")
	flagFileFilter            = flag.String("file-filter", "", "supply a text file with newline separated filenames to process")
	flagVersion               = flag.Bool("version", false, "print version")
	flagZScore                = flag.Bool("zscore", false, "use zscore for normalization")
	flagEncode                = flag.Bool("encode", true, "encode the values to numeric format")
	flagEncodeCategoricals    = flag.Bool("encodeCategoricals", true, "encode the categorical values to numeric format")
	flagNormalizeCategoricals = flag.Bool("normalizeCategoricals", true, "normalize the categorical values after encoding them to numeric format")
)
