package main

// simple labeling for CSV files from the SWaT 2015 Network CSV dataset
// usage for testing:
// go run label-2015-dataset.go data/2015-12-22_034215_69.log.part01_sorted.csv data/List_of_attacks_Final-fixed.csv
// build:
// GOOS=linux go build -o bin/label-2015-dataset label-2015-dataset.go
// server: cd /datasets/SWaT/01_SWaT_Dataset_Dec\ 2015/Network
// label-2015-dataset -attacks List_of_attacks_Final-fixed.csv -out /home/***REMOVED***/labeled-SWaT-2015-network

import (
	"encoding/json"
	"flag"
	"fmt"
	"io/ioutil"
	"log"
	"os"
	"path/filepath"

	"strings"
	"sync"
	"time"
)

var inputHeader = []string{
	"num",
	"date",
	"time",
	"orig",
	"type",
	"i/f_name",
	"i/f_dir",
	"src",
	"dst",
	"proto",
	"appi_name",
	"proxy_src_ip",
	"Modbus_Function_Code",
	"Modbus_Function_Description",
	"Modbus_Transaction_ID",
	"SCADA_Tag",
	"Modbus_Value",
	"service",
	"s_port",
	"Tag",
	//"Normal/Attack",
}
var inputHeaderLen = len(inputHeader)

var outputHeader = []string{
	"timestamp",
	"orig",
	"type",
	"i/f_name",
	"i/f_dir",
	"src",
	"dst",
	"proto",
	"appi_name",
	"proxy_src_ip",
	"Modbus_Function_Code",
	"Modbus_Function_Description",
	"Modbus_Transaction_ID",
	"SCADA_Tag",
	"Modbus_Value",
	"service",
	"s_port",
	"Normal/Attack",
}
var outputHeaderLen = len(outputHeader)

/*
 * Globals
 */

var (
	// stats about applied labels
	hitMap     = make(map[string]int)
	hitMapLock sync.Mutex

	// attack information for mapping
	attacks []*attack

	// worker pool
	workers []chan task
	next    int

	results     = make(map[string]*fileSummary)
	resultMutex sync.Mutex

	colSums map[string]columnSummary
)

/*
 * Main
 */

func main() {

	flag.Parse()

	if *flagAttackList != "" {
		attacks = parseAttackList(*flagAttackList)
	}

	var (
		files []string
		start = time.Now()
		wg    sync.WaitGroup
	)

	err := filepath.Walk(*flagInput, func(path string, info os.FileInfo, err error) error {

		if strings.HasSuffix(path, *flagPathSuffix) {
			files = append(files, path)
		}

		return nil
	})
	if err != nil {
		panic(err)
	}

	totalFiles := len(files)
	fmt.Println("collected", totalFiles, "CSV files for labeling, num workers:", *flagNumWorkers)
	fmt.Println("new CSV header:", outputHeader)
	fmt.Println("output directory:", *flagOut)
	fmt.Println("initializing", *flagNumWorkers, "workers")

	// spawn workers
	for i := 0; i < *flagNumWorkers; i++ {
		workers = append(workers, worker())
	}

	// set max files
	if *flagMaxFiles == 0 {
		*flagMaxFiles = len(files)
	}

	if *flagColumnSummaries != "" {

		data, err := ioutil.ReadFile(*flagColumnSummaries)
		if err != nil {
			log.Fatal(err)
		}

		err = json.Unmarshal(data, &colSums)
		if err != nil {
			log.Fatal("failed to unmarshal json", err)
		}

		fmt.Println("loaded column summaries:", len(colSums))

		runLabeling(files, &wg, totalFiles)
		return
	}

	// analyze task
	for current, file := range files[:*flagMaxFiles] {
		wg.Add(1)
		handleTask(task{
			typ:        typeAnalyze,
			file:       file,
			current:    current,
			totalFiles: totalFiles,
			wg:         &wg,
		})
	}

	fmt.Println("started all analysis jobs, waiting...")
	wg.Wait()

	printAnalysisInfo()

	if *flagAnalyzeOnly {
		fmt.Println("done in", time.Since(start))
		return
	}

	// run labeling
	runLabeling(files, &wg, totalFiles)

	fmt.Println("done in", time.Since(start))
}
