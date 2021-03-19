package main

// simple dataset cleaner for the SWaT 2015 Physical Attack data file: SWaT_Dataset_Attack_v0.csv

// compile:
// $ go build -o bin/fix-swat-dataset fix-swat-dataset.go

// use:
// $ bin/fix-swat-dataset SWaT_Dataset_Attack_v0.csv

import (
	"bufio"
	"fmt"
	"io"
	"log"
	"os"
	"strconv"
	"strings"
	"time"
)

// ClearLine clears the current line of the terminal
func clearLine() {
	print("\033[2K\r")
}

func main() {

	inFile, err := os.Open(os.Args[1])
	if err != nil {
		log.Fatal(err)
	}
	defer inFile.Close()

	outFileName := strings.TrimSuffix(os.Args[1], ".csv") + "-fixed.csv"

	fmt.Println("outFileName", outFileName)

	outFile, err := os.Create(outFileName)
	if err != nil {
		log.Fatal(err)
	}
	defer outFile.Close()

	var (
		elemCount = 0
		r         = bufio.NewReader(inFile)
		count     = 0
	)

	for {
		line, _, err := r.ReadLine()
		if err == io.EOF {
			fmt.Println()
			return
		}
		if err != nil {
			log.Fatal(err)
		}

		parts := strings.Split(string(line), ",")
		//fmt.Println(parts)

		count++
		
		// skip header
		if count == 1 {
			elemCount = len(parts) - 1	

			_, err = outFile.WriteString(strings.Join(parts, ",") + "\n")
			if err != nil {
				log.Fatal(err)
			}

			continue
		}

		if count%1000 == 0 {
			clearLine()
			fmt.Print("processed ", count, " lines")
		}

		ts := strings.Trim(parts[0], "\" ")

		// convert timestamp to UNIX
		t, err := time.Parse("2/1/2006 15:04:05 PM", ts)
		if err != nil {
			log.Fatal(count, err)
		}
		parts[0] = strconv.FormatInt(t.Unix(), 10)

		// fix label if incorrect
		if parts[elemCount] == "\"A ttack\"" {
			parts[elemCount] = "Attack"
		}

		// write to new file
		_, err = outFile.WriteString(strings.Join(parts, ",") + "\n")
		if err != nil {
			log.Fatal(err)
		}
	}
}
