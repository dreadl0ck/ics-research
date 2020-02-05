package main

import (
	"fmt"
	"sort"
	"strconv"
	"time"

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

type columnType int

const (
	typeString columnType = iota
	typeNumeric
)

func (c columnType) String() string {
	switch c {
	case typeNumeric:
		return "numeric"
	case typeString:
		return "string"
	default:
		return "invalid"
	}
}

type columnSummary struct {
	Version       string     `json:"version"`
	Col           string     `json:"col"`
	Typ           columnType `json:"typ"`
	UniqueStrings []string   `json:"uniqueStrings"`
	Std           float64    `json:"std"`
	Mean          float64    `json:"mean"`
	Min           float64    `json:"min"`
	Max           float64    `json:"max"`
}

func merge(results map[string]*fileSummary) map[string]columnSummary {

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
		return nil
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

		if *flagDebug {
			fmt.Println(ansi.Red+sum.file, "len(sum.columns):", len(sum.columns), "len(sum.strings):", len(sum.strings), ansi.Reset)
			time.Sleep(1 * time.Second)
		}

		for col, values := range sum.strings {
			if *flagDebug {
				fmt.Println("column:", col, sum.file, sum.columns, len(sum.columns))
			}
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

	var colSums = make(map[string]columnSummary)

	for col, data := range d.strings {
		fmt.Println(ansi.Yellow, "> column:", col, "unique_values:", len(data), ansi.Reset)

		// lookup type for column
		isString := stringColumns[col]

		if isString {
			var unique []string
			for value := range data {
				unique = append(unique, value)
			}
			length := len(unique)

			if col != "Modbus_Value" && col != "time" {
				for _, v := range unique {
					fmt.Println("   -", v)
				}
			}

			values := makeIntSlice(length)
			mean, std := stat.MeanStdDev(values, nil)
			fmt.Println(col, "mean:", mean, "stddev:", std)

			colSums[col] = columnSummary{
				Version:       version,
				Col:           col,
				Typ:           typeString,
				UniqueStrings: unique,
				Mean:          mean,
				Std:           std,
				Min:           0,
				Max:           float64(length) - 1,
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

			min, max := minMaxIntArr(values)

			colSums[col] = columnSummary{
				Version: version,
				Col:     col,
				Typ:     typeNumeric,
				Mean:    mean,
				Std:     std,
				Min:     min,
				Max:     max,
			}
		}
	}

	fmt.Println("skipped lines with missing values:", skipped)

	return colSums
}
