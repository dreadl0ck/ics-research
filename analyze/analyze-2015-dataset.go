package main

// simple labeling for CSV files from the SWaT 2015 Network CSV dataset
// usage for testing:
// go run label-2015-dataset.go data/2015-12-22_034215_69.log.part01_sorted.csv data/List_of_attacks_Final-fixed.csv
// build:
// GOOS=linux go build -o bin/label-2015-dataset label-2015-dataset.go
// server: cd /datasets/SWaT/01_SWaT_Dataset_Dec\ 2015/Network
// label-2015-dataset -attacks List_of_attacks_Final-fixed.csv -out /home/***REMOVED***/labeled-SWaT-2015-network

import (
	"encoding/csv"
	"flag"
	"fmt"
	"io"
	"log"
	"os"
	"path/filepath"

	//"sort"
	"github.com/mgutz/ansi"
	"gonum.org/v1/gonum/stat"
	"strconv"
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
	// commandline flags
	flagAttackList = flag.String("attacks", "", "attack list CSV")
	flagInput      = flag.String("in", ".", "input directory (default is current directory)")
	flagOut        = flag.String("out", ".", "output path")
	flagNumWorkers = flag.Int("workers", 100, "number of parallel processed files")
	flagMaxFiles   = flag.Int("max", 0, "max number of processed files")
	flagDebug      = flag.Bool("debug", false, "toggle debug mode")

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

	defer func() {
		fmt.Println("done in", time.Since(start))
	}()

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

	d := &datasetSummary{
		strings: make(map[string]map[string]int),
	}

	// init colums map
	for _, sum := range results {
		for col, _ := range sum.strings {
			d.strings[col] = make(map[string]int)
		}
		break
	}

	var skipped int

	// merge results
	for _, sum := range results {

		//fmt.Println(file, sum)
		skipped += sum.skipped

		d.fileCount++
		d.lineCount += sum.lineCount
		d.columns = sum.columns

		for col, values := range sum.strings {
			for key, num := range values {
				d.strings[col][key] += num
			}
		}
	}

	fmt.Println(ansi.Red+"DONE", "lines", d.lineCount, "files", d.fileCount, "cols", d.columns, ansi.Reset)

	//spew.Dump(d)

	for col, data := range d.strings {
		fmt.Println(ansi.Yellow, "col", col, "len(data)", len(data), ansi.Reset)

		// determine if column contains string or numeric data
		isString := true

		// peek at first elem
		for value := range data {
			_, err := strconv.Atoi(value)
			if err != nil {
				_, err := strconv.ParseFloat(value, 64)
				if err == nil {
					isString = false
				}
			} else {
				isString = false
			}
			break
		}

		if isString {
			var unique []string
			for value := range data {
				unique = append(unique, value)
			}

			if col != "Modbus_Value" && col != "time" {
				fmt.Println(unique)
			}
		} else {

			var values []float64

			// create series over all data points
			for value, num := range data {

				v, err := strconv.ParseFloat(value, 64)
				if err != nil {
					fmt.Println("failed to parse float in col "+col+", error: ", err, value)
					continue
				}

				for i := 0; i < num; i++ {
					values = append(values, v)
				}
			}

			mean, std := stat.MeanStdDev(values, nil)
			fmt.Println(col, "mean:", mean, "stddev:", std)
		}
	}

	fmt.Println("skipped lines with missing values:", skipped)
}

// attackResults implements the sort.Sort interface

type attackResults []attackResult

type attackResult struct {
	name string
	hits int
}

func (s attackResults) Len() int {
	return len(s)
}
func (s attackResults) Swap(i, j int) {
	s[i], s[j] = s[j], s[i]
}
func (s attackResults) Less(i, j int) bool {
	return s[i].hits < s[j].hits
}

/*
 * Utils
 */

// ClearLine clears the current line of the terminal
func clearLine() {
	print("\033[2K\r")
}

/*
 * Attack
 */

type attack struct {
	AttackNumber   int
	StartTime      time.Time
	EndTime        time.Time
	AttackDuration time.Duration
	AttackPoints   []string
	Adresses       []string
	AttackName     string
	AttackType     string
	Intent         string
	ActualChange   string
	Notes          string
}

func (a attack) affectsHosts(src, dst string) bool {
	for _, addr := range a.Adresses {
		if addr == src || addr == dst {
			return true
		}
	}
	return false
}

func (a attack) during(t time.Time) bool {
	if a.StartTime.Equal(t) || a.EndTime.Equal(t) {
		return true
	}

	if a.StartTime.Before(t) && a.EndTime.After(t) {
		return true
	}

	return false
}

// Attack information parsing
// parses a CSV file that contains the attack timestamps and descriptions
/*
func parseAttackList(path string) (labels []*attack) {

	fmt.Println("parsing attacks in", path)

	// open input file
	f, err := os.Open(path)
	if err != nil {
		log.Fatal(err)
	}
	defer f.Close()

	// create CSV file reader
	r := csv.NewReader(f)
	records, err := r.ReadAll()
	if err != nil {
		log.Fatal(err)
	}

	// fields Attack Info:
	// 0  AttackNumber
	// 1  AttackNumberOriginal
	// 2  StartTime
	// 3  EndTime
	// 4  AttackDuration
	// 5  AttackPoints
	// 6  Adresses
	// 7  AttackName
	// 8  AttackType
	// 9  Intent
	// 10 ActualChange
	// 11 Notes
	for _, record := range records[1:] {

		// fmt.Println("processing attack record:", i+1)

		num, err := strconv.Atoi(record[0])
		if err != nil {
			log.Fatal("failed to parse attack number:", err)
		}

		start, err := strconv.ParseInt(record[2], 10, 64)
		if err != nil {
			log.Fatal("failed to parse start time as UNIX timestamp:", err)
		}

		end, err := strconv.ParseInt(record[3], 10, 64)
		if err != nil {
			log.Fatal("failed to parse end time as UNIX timestamp:", err)
		}

		duration, err := time.ParseDuration(record[4])
		if err != nil {
			log.Fatal("failed to parse duration:", err)
		}

		toArr := func(input string) []string {
			return strings.Split(strings.Trim(input, "\""), ",")
		}

		atk := &attack{
			AttackNumber:   num,                 // int
			StartTime:      time.Unix(start, 0), // time.Time
			EndTime:        time.Unix(end, 0),   // time.Time
			AttackDuration: duration,            // time.Duration
			AttackPoints:   toArr(record[5]),    // []string
			Adresses:       toArr(record[6]),    // []string
			AttackName:     record[7],           // string
			AttackType:     record[8],           // string
			Intent:         record[9],           // string
			ActualChange:   record[10],          // string
			Notes:          record[11],          // string
		}

		// ensure no alerts with empty name are collected
		if atk.AttackName == "" || atk.AttackName == " " {
			fmt.Println("skipping entry with empty name", atk)
			continue
		}

		// append to collected alerts
		labels = append(labels, atk)
	}

	return
}*/

/*
 * Task
 */

type task struct {
	file                string
	current, totalFiles int
	wg                  *sync.WaitGroup
}

func handleTask(t task) {

	// make it work for 1 worker only
	if len(workers) == 1 {
		workers[0] <- t
		return
	}

	// send the packetInfo to the encoder routine
	workers[next] <- t

	// increment or reset next
	if next+1 >= *flagNumWorkers {
		// reset
		next = 1
	} else {
		next++
	}
}

// worker spawns a new worker goroutine
// and returns a channel for receiving input packets.
func worker() chan task {

	// init channel to receive paths
	chanInput := make(chan task)

	// start worker
	go func() {
		for {
			select {
			case t := <-chanInput:
				s := t.analyze()
				resultMutex.Lock()
				results[t.file] = s
				resultMutex.Unlock()
				continue
			}
		}
	}()

	// return input channel
	return chanInput
}

// For strings: num variants
// For nums: stddev, mean, min, max
type fileSummary struct {
	file string

	lineCount int

	columns []string

	// mapped column names to number of hits for each unique string
	strings map[string]map[string]int

	// mapped column names to number of hits for each unique value
	//nums map[string]map[float64]int

	skipped int
}

type datasetSummary struct {
	fileCount int
	lineCount int

	columns []string

	// mapped column names to number of hits for each unique string
	strings map[string]map[string]int
}

func (t task) analyze() *fileSummary {

	info := "[" + strconv.Itoa(t.current+1) + "/" + strconv.Itoa(t.totalFiles) + "]"
	fmt.Println(info, "processing", t.file)

	inputFile, err := os.Open(t.file)
	if err != nil {
		log.Fatal(err)
	}
	defer inputFile.Close()

	s := &fileSummary{
		file:    t.file,
		strings: make(map[string]map[string]int),
		//nums:    make(map[string]map[float64]int),
	}

	// var outFileName = strings.TrimSuffix(t.file, ".csv") + "-labeled.csv"
	// if *flagOut != "." {
	// 	outFileName = filepath.Join(*flagOut, outFileName)
	// }

	// outputFile, err := os.Create(outFileName)
	// if err != nil {
	// 	log.Fatal(err)
	// }
	// defer outputFile.Close()

	var (
		inputReader = csv.NewReader(inputFile)
		//outputWriter      = csv.NewWriter(outputFile)
		//numMatches int
		count   int
		skipped int
	)

	// // write header
	// err = outputWriter.Write(header)
	// if err != nil {
	// 	log.Fatal(err)
	// }

	for {
		r, err := inputReader.Read()
		if err == io.EOF {
			break
		}
		if err != nil {
			fmt.Println("error while reading next line from file", t.file, "error:", err)
			count++
			continue
		}
		count++

		// skip header
		if count == 1 {
			s.columns = r
			continue
		}

		skip := false
		for index, v := range r {
			if v == "" || v == " " {
				if *flagDebug {
					fmt.Println(t.file, "skipping record", count, "due to missing field for column", s.columns[index])
				}

				//fmt.Println(r)
				skipped++
				count++
				skip = true
			}
		}
		if skip {
			continue
		}

		// fields Network CSV:
		// 0  num
		// 1  date
		// 2  time
		// 3  orig
		// 4  type
		// 5  i/f_name
		// 6  i/f_dir
		// 7  src
		// 8  dst
		// 9  proto
		// 10 appi_name
		// 11 proxy_src_ip
		// 12 Modbus_Function_Code
		// 13 Modbus_Function_Description
		// 14 Modbus_Transaction_ID
		// 15 SCADA_Tag
		// 16 Modbus_Value
		// 17 service
		// 18 s_port
		// 19 Tag
		// num,date,time,orig,type,i/f_name,i/f_dir,src,dst,proto,appi_name,proxy_src_ip,Modbus_Function_Code,Modbus_Function_Description,Modbus_Transaction_ID,SCADA_Tag,Modbus_Value,service,s_port,Tag
		// 1,21Dec2015,22:17:56,192.168.1.48,log,eth1,outbound,192.168.1.60,192.168.1.10,tcp,CIP_read_tag_service,192.168.1.60,76,Read Tag Service,30721,HMI_LIT101,Number of Elements: 1,44818,53260,0

		for i, col := range s.columns {
			// TODO: check if number or string
			if _, ok := s.strings[col]; !ok {
				s.strings[col] = make(map[string]int)
				s.strings[col][r[i]]++
			} else {
				s.strings[col][r[i]]++
			}
		}

		//var classification = "normal"
		//
		//ti, err := time.Parse("2Jan200615:04:05", r[1]+r[2])
		//if err != nil {
		//	ti, err = time.Parse("2Jan0615:04:05", r[1]+r[2])
		//	if err != nil {
		//		ti, err = time.Parse("2-Jan-0615:04:05", r[1]+r[2])
		//		if err != nil {
		//			log.Println(info, err, "file:", t.file, "line:", count)
		//			sec, err := strconv.ParseInt(r[1]+r[2], 10, 64)
		//			if err != nil {
		//				fmt.Println(info, " no valid timestamp format found!", t.file)
		//				continue
		//			}
		//			ti = time.Unix(sec, 0)
		//		}
		//	}
		//}
		// fmt.Println(r[1]+r[2], "time:", t)

		//for _, a := range attacks {
		//	if a.during(ti) {
		//		if a.affectsHosts(r[7], r[8]) {
		//			classification = a.AttackType
		//			//fmt.Println("match for", a.AttackName)
		//
		//			hitMapLock.Lock()
		//			hitMap[a.AttackName]++
		//			hitMapLock.Unlock()
		//
		//			numMatches++
		//			break
		//		}
		//	}
		//}
		//
		//final := append(r, classification)
		//if len(final) == 22 {
		//
		//	// remove empty column in some of the provided CSV data
		//	final[19] = final[20]
		//	final[20] = final[21]
		//
		//	// remove last elem
		//	final = final[:21]
		//}
		//
		//// ensure no corrupted data is written into the output file
		//if len(final) != headerLen {
		//	fmt.Println(info, "file:", t.file, "line:", count)
		//	log.Fatal("length of data line does not match header length:", len(final), "!=", len(header))
		//}

		// err = outputWriter.Write(final)
		// if err != nil {
		// 	log.Fatal(err)
		// }
	}

	// outputWriter.Flush()
	// err = outputWriter.Error()
	// if err != nil {
	// 	log.Fatal(err)
	// }

	//fmt.Println(info, count, "records,", numMatches, "attacks written to", filepath.Base(outputFile.Name()))
	t.wg.Done()
	s.lineCount = count - 1 // -1 for the CSV header
	s.skipped = skipped

	return s
}
