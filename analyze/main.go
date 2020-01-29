package main

// simple labeling for CSV files from the SWaT 2015 Network CSV dataset
// usage for testing:
// go run label-2015-dataset.go data/2015-12-22_034215_69.log.part01_sorted.csv data/List_of_attacks_Final-fixed.csv
// build:
// GOOS=linux go build -o bin/label-2015-dataset label-2015-dataset.go
// server: cd /datasets/SWaT/01_SWaT_Dataset_Dec\ 2015/Network
// label-2015-dataset -attacks List_of_attacks_Final-fixed.csv -out /home/***REMOVED***/labeled-SWaT-2015-network

import (
	"flag"
	"fmt"
	"os"
	"path/filepath"

	//"sort"

	"strings"
	"sync"
	"time"
)

var header = []string{
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
	"Normal/Attack",
}
var headerLen = len(header)

/*
 * Globals
 */

var (
	// stats about applied labels
	hitMap     = make(map[string]int)
	hitMapLock sync.Mutex

	// attack information for mapping
	//attacks []*attack

	// worker pool
	workers []chan task
	next    int

	results     = make(map[string]*fileSummary)
	resultMutex sync.Mutex
)

/*
 * Main
 */

func main() {

	flag.Parse()

	//if *flagAttackList == "" {
	//	log.Fatal("need an attack CSV for labeling")
	//}
	//attacks = parseAttackList(*flagAttackList)

	var (
		files []string
		start = time.Now()
		wg    sync.WaitGroup
	)

	err := filepath.Walk(*flagInput, func(path string, info os.FileInfo, err error) error {

		if strings.HasSuffix(path, "-labeled.csv") {
			files = append(files, path)
		}

		return nil
	})
	if err != nil {
		panic(err)
	}

	totalFiles := len(files)
	fmt.Println("collected", totalFiles, "CSV files for labeling, num workers:", *flagNumWorkers)

	fmt.Println("new CSV header:", header)
	fmt.Println("output directory:", *flagOut)
	fmt.Println("initializing", *flagNumWorkers, "workers")

	for i := 0; i < *flagNumWorkers; i++ {
		workers = append(workers, worker())
	}

	if *flagMaxFiles == 0 {
		*flagMaxFiles = len(files)
	}
	for current, file := range files[:*flagMaxFiles] {
		wg.Add(1)
		handleTask(task{
			file:       file,
			current:    current,
			totalFiles: totalFiles,
			wg:         &wg,
		})
	}

	fmt.Println("started all jobs, waiting...")
	wg.Wait()

	analyze(results)

	//// sort and print mapping stats
	//var atks attackResults
	//for n, hits := range hitMap {
	//	atks = append(atks, attackResult{
	//		name: n,
	//		hits: hits,
	//	})
	//}
	//
	//sort.Sort(atks)
	//
	//var rows [][]string
	//for _, a := range atks {
	//	rows = append(rows, []string{strconv.Itoa(a.hits), a.name})
	//}

	//tui.Table(os.Stdout, []string{"Hits", "AttackName"}, rows)
	//
	//// print names of attacks that could not be mapped
	//var notMatched []string
	//for _, a := range attacks {
	//	if _, ok := hitMap[a.AttackName]; !ok {
	//		notMatched = append(notMatched, a.AttackName)
	//	}
	//}
	//if len(notMatched) > 0 {
	//	fmt.Println("could not map the following attacks:")
	//}
	//for _, name := range notMatched {
	//	fmt.Println("-", name)
	//}

	// for file, sum := range results {
	// 	fmt.Println(file, sum)
	// }

	fmt.Println("done in", time.Since(start))
}
