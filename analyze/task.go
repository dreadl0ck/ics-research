package main

import (
	"encoding/csv"
	"fmt"
	"io"
	"log"
	"os"
	"strconv"
	"sync"
)

type correction struct {
	old string
	new string
}

func newCorrection(old, new string) correction {
	return correction{
		old: old,
		new: new,
	}
}

// columns mapped to corrections
var cmap = map[string][]correction{
	"proxy_src_ip": []correction{
		newCorrection("192.16:.1.10", "192.168.1.10"),
	},
	"type": []correction{
		newCorrection("loe", "log"),
	},
	"Modbus_Function_Description": []correction{
		newCorrection("Read Tag Service - Responqe", "Read Tag Service - Response"),
	},
}

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
	chanInput := make(chan task, 1)

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

	attacks int

	uniqueAttacks map[string]struct{}
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
		file:          t.file,
		strings:       make(map[string]map[string]int),
		uniqueAttacks: make(map[string]struct{}),
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
		attacks int
	)
	if *flagReuseLineBuffer {
		inputReader.ReuseRecord = true
	}

	// // write header
	// err = outputWriter.Write(header)
	// if err != nil {
	// 	log.Fatal(err)
	// }

	var (
		r          []string
		lastRecord int
	)

	for {
		r, err = inputReader.Read()
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
			s.columns = make([]string, len(r))

			// copy header, to allow reusing the record slice
			for i, elem := range r {
				s.columns[i] = elem
			}

			lastRecord = len(r) - 1
			continue
		}

		if *flagCountAttacks {
			if r[lastRecord] != "normal" {
				attacks++
				s.uniqueAttacks[r[lastRecord]] = struct{}{}
				continue
			}
		}

		if *flagSkipIncompleteRecords {
			skip := false
			for index, v := range r {
				if v == "" || v == " " {

					if *flagDebug {
						fmt.Println(t.file, "skipping record", count, "due to missing field for column", s.columns[index], "label:", r[len(r)-1])
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
		}
		if *flagZeroIncompleteRecords {
			for index, v := range r {
				if v == "" || v == " " {
					r[index] = "0"
				}
			}
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

			if excluded(col) {
				continue
			}

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
	s.attacks = attacks

	return s
}

var excludedCols = []string{"num", "date", "time"}

func excluded(col string) bool {
	for _, n := range excludedCols {
		if n == col {
			return true
		}
	}
	return false
}
