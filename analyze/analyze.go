package main

import (
	"fmt"
	"sort"
	"strconv"

	"github.com/mgutz/ansi"
	"gonum.org/v1/gonum/stat"
)

var stringColumns = map[string]bool{
	"SCADA_Tag":                   true,
	"type":                        true,
	"orig":                        true,
	"Modbus_Value":                true,
	"proxy_src_ip":                true,
	"proto":                       true,
	"src":                         true,
	"i/f_name":                    true,
	"Modbus_Function_Description": true,
	"appi_name":                   true,
	"i/f_dir":                     true,
	"Normal/Attack":               true,
	"dst":                         true,
}

func analyze(results map[string]*fileSummary) {

	if *flagCountAttacks {
		var attackFiles sort.StringSlice

		for _, sum := range results {
			if sum.attacks != 0 {
				attackFiles = append(attackFiles, sum.file)
			}
		}

		attackFiles.Sort()

		for _, file := range attackFiles {
			sum := results[file]
			var uniqueAttacks []string
			for a := range sum.uniqueAttacks {
				uniqueAttacks = append(uniqueAttacks, a)
			}
			fmt.Println(file, ":", sum.attacks, uniqueAttacks)
		}
		return
	}

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

		//fmt.Println(sum.file, sum.columns)

		for col, values := range sum.strings {
			for key, num := range values {
				d.strings[col][key] += num
			}
		}
	}

	fmt.Println(ansi.Red + "DONE")
	fmt.Println("files:", d.fileCount)
	fmt.Println("lines:", d.lineCount)
	fmt.Println("columns", d.columns, ansi.Reset)
	//spew.Dump(d)

	for col, data := range d.strings {
		fmt.Println(ansi.Yellow, "> column:", col, "unique_values:", len(data), ansi.Reset)

		// determine if column contains string or numeric data
		//isString := true

		// peek at first elem
		// for value := range data {
		// 	_, err := strconv.Atoi(value)
		// 	if err != nil {
		// 		_, err := strconv.ParseFloat(value, 64)
		// 		if err == nil {
		// 			isString = false
		// 		}
		// 	} else {
		// 		isString = false
		// 	}
		// 	break
		// }

		// lookup type for column
		isString := stringColumns[col]

		if isString {
			var unique []string
			for value := range data {
				unique = append(unique, value)
			}

			if col != "Modbus_Value" && col != "time" {
				for _, v := range unique {
					fmt.Println("   -", v)
				}
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

			if col == "Tag" {
				fmt.Println(data)
			}

			mean, std := stat.MeanStdDev(values, nil)
			fmt.Println(col, "mean:", mean, "stddev:", std)
		}
	}

	fmt.Println("skipped lines with missing values:", skipped)
}
