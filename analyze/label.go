package main

import (
	"encoding/csv"
	"fmt"
	"io"
	"log"
	"os"
	"path/filepath"
	"strconv"
	"strings"
	"time"
)

// 1) correct fields
// 2) encode columns
// 3) add labels
func (t task) label() {

	info := "[" + strconv.Itoa(t.current+1) + "/" + strconv.Itoa(t.totalFiles) + "]"
	fmt.Println(info, "processing", t.file)

	inputFile, err := os.Open(t.file)
	if err != nil {
		log.Fatal(err)
	}
	defer inputFile.Close()

	var outFileName = strings.TrimSuffix(t.file, ".csv") + "-labeled.csv"
	if *flagOut != "." {
		outFileName = filepath.Join(*flagOut, outFileName)
	}

	outputFile, err := os.Create(outFileName)
	if err != nil {
		log.Fatal(err)
	}
	defer outputFile.Close()

	var (
		inputReader  = csv.NewReader(inputFile)
		outputWriter = csv.NewWriter(outputFile)
		numMatches   int
		count        int
		//skipped      int
	)
	if *flagReuseLineBuffer {
		inputReader.ReuseRecord = true
	}

	// write header
	err = outputWriter.Write(outputHeader)
	if err != nil {
		log.Fatal(err)
	}

	var (
		r []string
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
			continue
		}

		// if *flagSkipIncompleteRecords {
		// 	skip := false
		// 	for index, v := range r {
		// 		if v == "" || v == " " {

		// 			if *flagDebug {
		// 				fmt.Println(t.file, "skipping record", count, "due to missing field for column", s.columns[index], "label:", r[len(r)-1])
		// 			}

		// 			//fmt.Println(r)
		// 			skipped++
		// 			count++
		// 			skip = true
		// 		}
		// 	}
		// 	if skip {
		// 		continue
		// 	}
		// }
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

		// example:
		// num,date,time,orig,type,i/f_name,i/f_dir,src,dst,proto,appi_name,proxy_src_ip,Modbus_Function_Code,Modbus_Function_Description,Modbus_Transaction_ID,SCADA_Tag,Modbus_Value,service,s_port,Tag
		// 1,21Dec2015,22:17:56,192.168.1.48,log,eth1,outbound,192.168.1.60,192.168.1.10,tcp,CIP_read_tag_service,192.168.1.60,76,Read Tag Service,30721,HMI_LIT101,Number of Elements: 1,44818,53260,0

		var classification = "normal"

		ti, err := time.Parse("2Jan200615:04:05", r[1]+r[2])
		if err != nil {
			ti, err = time.Parse("2Jan0615:04:05", r[1]+r[2])
			if err != nil {
				ti, err = time.Parse("2-Jan-0615:04:05", r[1]+r[2])
				if err != nil {
					log.Println(info, err, "file:", t.file, "line:", count)
					sec, err := strconv.ParseInt(r[1]+r[2], 10, 64)
					if err != nil {
						fmt.Println(info, " no valid timestamp format found!", t.file)
						continue
					}
					ti = time.Unix(sec, 0)
				}
			}
		}
		fmt.Println(r[1]+r[2], "time:", t)

		// determine classification
		for _, a := range attacks {
			if a.during(ti) {
				if a.affectsHosts(r[7], r[8]) {
					classification = a.AttackType
					//fmt.Println("match for", a.AttackName)

					hitMapLock.Lock()
					hitMap[a.AttackName]++
					hitMapLock.Unlock()

					numMatches++
					break
				}
			}
		}

		// fix empty column in dataset
		if len(r) == 21 {

			// remove empty column in some of the provided CSV data
			r[18] = r[19]
			r[19] = r[20]

			// remove last elem
			r = r[:20]
		}

		// apply value corrections
		for index, v := range r {
			if corr, ok := cmap[inputHeader[index]]; ok {
				for _, c := range corr {
					if v == c.old {
						r[index] = c.new
					}
				}
			}
		}

		// encode values
		for index, v := range r {
			colName := inputHeader[index]
			if sum, ok := colSums[colName]; ok {
				switch sum.Typ {
				case typeString:
					r[index] = getIndex(sum.UniqueStrings, v)
				case typeNumeric:

					i, err := strconv.ParseFloat(v, 64)
					if err != nil {
						ii, err := strconv.Atoi(v)
						if err != nil {
							log.Fatal("failed to parse number:", v, t.file, count)
						}
						i = float64(ii)
					}

					// normalize with z_score
					r[index] = strconv.FormatFloat((i-sum.Mean)/sum.Std, 'f', 5, 64)
				}
			}
		}

		// remove leading num and date columns
		r = r[2:]

		// and add timestamp to time column
		r[2] = strconv.FormatInt(ti.Unix(), 10)

		// remove Tag column, and append classification
		final := append(r[:len(r)-1], classification)

		// ensure no corrupted data is written into the output file
		if len(final) != outputHeaderLen {
			fmt.Println(info, "file:", t.file, "line:", count)
			log.Fatal("length of data line does not match header length:", len(final), "!=", len(outputHeader))
		}

		err = outputWriter.Write(final)
		if err != nil {
			log.Fatal(err)
		}
	}

	outputWriter.Flush()
	err = outputWriter.Error()
	if err != nil {
		log.Fatal(err)
	}

	fmt.Println(info, count, "records,", numMatches, "attacks written to", filepath.Base(outputFile.Name()))
	t.wg.Done()
}
