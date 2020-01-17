package main

// simple labeling for CSV files from the SWaT 2015 Network CSV dataset
// usage:
// go run label-2015-dataset.go data/2015-12-22_034215_69.log.part01_sorted.csv data/List_of_attacks_Final-fixed.csv

import (
	"encoding/csv"
	"flag"
	"fmt"
	"io"
	"log"
	"os"
	"path/filepath"
	"strconv"
	"strings"
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

// Utils

// ClearLine clears the current line of the terminal
func clearLine() {
	print("\033[2K\r")
}

var (
	flagAttackList = flag.String("attacks", "", "attack list CSV")
	flagDir        = flag.String("dir", ".", "input directory (default is current directory)")
)

func main() {

	flag.Parse()

	if *flagAttackList == "" {
		log.Fatal("need an attack CSV for labeling")
	}

	var (
		attacks = ParseAttackList(*flagAttackList)
		files   []string
		start   = time.Now()
	)

	defer func() {
		fmt.Println("done in", time.Since(start))
	}()

	err := filepath.Walk(*flagDir, func(path string, info os.FileInfo, err error) error {

		if filepath.Ext(path) == ".csv" {
			files = append(files, path)
		}

		return nil
	})
	if err != nil {
		panic(err)
	}

	totalFiles := len(files)
	fmt.Println("collected", totalFiles, "CSV files to label")

	fmt.Println("new CSV header:", header)

	for current, file := range files {

		fmt.Println("[", current+1, "/", totalFiles, "]", "processing", file)

		inputFile, err := os.Open(file)
		if err != nil {
			log.Fatal(err)
		}
		defer inputFile.Close()

		outFileName := strings.TrimSuffix(file, ".csv") + "-labeled.csv"

		outputFile, err := os.Create(outFileName)
		if err != nil {
			log.Fatal(err)
		}
		defer outputFile.Close()

		var (
			inputReader       = csv.NewReader(inputFile)
			outputWriter      = csv.NewWriter(outputFile)
			numMatches, count int
		)

		// write header
		err = outputWriter.Write(header)
		if err != nil {
			log.Fatal(err)
		}

		for {
			r, err := inputReader.Read()
			if err == io.EOF {
				break
			}
			if err != nil {
				log.Fatal(err)
			}

			count++

			// skip header
			if count == 1 {
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

			var classification = "normal"

			t, err := time.Parse("2Jan200615:04:05", r[1]+r[2])
			if err != nil {
				log.Fatal(count, err)
			}
			// fmt.Println(r[1]+r[2], "time:", t)

			for _, a := range attacks {
				if a.during(t) {
					if a.affectsHosts(r[7], r[8]) {
						classification = a.AttackName
						fmt.Println("match for", a.AttackName)
						numMatches++
						break
					}
				}
			}

			err = outputWriter.Write(append(r, classification))
			if err != nil {
				log.Fatal(err)
			}
		}

		outputWriter.Flush()
		err = outputWriter.Error()
		if err != nil {
			log.Fatal(err)
		}

		fmt.Println("[", current+1, "/", totalFiles, "]", count, "records written to", outputFile.Name(), numMatches, "number of attacks labeled")
	}
}

func (a Attack) affectsHosts(src, dst string) bool {
	for _, addr := range a.Adresses {
		if addr == src || addr == dst {
			return true
		}
	}
	return false
}

func (a Attack) during(t time.Time) bool {
	if a.StartTime.Equal(t) || a.EndTime.Equal(t) {
		return true
	}

	if a.StartTime.Before(t) && a.EndTime.After(t) {
		return true
	}

	return false
}

type Attack struct {
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

func ParseAttackList(path string) (labels []*Attack) {

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

		atk := &Attack{
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
}
