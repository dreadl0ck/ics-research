package main

import (
	"encoding/csv"
	"fmt"
	"log"
	"os"
	"strconv"
	"strings"
	"time"
)

type stage struct {
	name    string
	addrs   []string
	devices []string
}

var stages = map[int]stage{
	1: stage{
		name:    "Raw Water",
		addrs:   []string{"192.168.1.10", "192.168.1.11", "192.168.0.10", "192.168.0.11"},
		devices: []string{"T101", "P101", "P102", "LIT101", "FIT101", "MV101"},
	},
	2: stage{
		name:    "Chemical Dosing",
		addrs:   []string{"192.168.1.20", "192.168.1.21", "192.168.0.20", "192.168.0.21"},
		devices: []string{"P201", "P202", "P203", "P204", "P205", "P206", "P207", "P208", "FIT201", "AIT201", "AIT202", "AIT203", "LS201", "LS202", "LS203", "MV201"},
	},
	3: stage{
		name:    "Ultrafiltration",
		addrs:   []string{"192.168.1.30", "192.168.1.31", "192.168.0.30", "192.168.0.31"},
		devices: []string{"T301", "P301", "P302", "LIT301", "FIT301", "FI301", "PSH301", "DPSH301", "DPIT301", "MV301", "MV302", "MV303", "MV304"},
	},
	4: stage{
		name:    "Dechlorination",
		addrs:   []string{"192.168.1.40", "192.168.1.41", "192.168.0.40", "192.168.0.41"},
		devices: []string{"T401", "P401", "P402", "P403", "P404", "UV401", "LIT401", "AIT401", "AIT402", "FIT401"},
	},
	5: stage{
		name:    "Reverse Osmosis",
		addrs:   []string{"192.168.1.50", "192.168.1.51", "192.168.0.50", "192.168.0.51"},
		devices: []string{"P501", "P502", "P503", "P504", "P505", "AIT501", "AIT502", "AIT503", "AIT504", "PSL501", "PSH501", "PIT501", "PIT502", "PIT503", "FIT503", "FIT504", "MV501", "MV502", "MV503", "MV504"},
	},
	6: stage{
		name:    "Reverse Osmosis permeate transfer, UF backwash",
		addrs:   []string{"192.168.1.60", "192.168.1.61", "192.168.0.60", "192.168.0.61"},
		devices: []string{"T601", "P601", "T602", "P602", "P603", "LS601", "LS602", "LS603", "FIT601", "FI601", "FI602"},
	},
}

var attackTypes = map[string][]int{
	"Single Stage Single Point": []int{1, 2, 3, 4, 6, 7, 8, 10, 11, 13, 14, 16, 17, 19, 20, 28, 31, 32, 33, 34, 36, 40, 41},
	"Single Stage Multi Point":  []int{21, 24, 25, 29, 35, 37},
	"Multi Stage Single Point":  []int{26, 27, 38, 39},
	"Multi Stage Multi Point":   []int{22, 23, 30},
}

func main() {

	inputFile, err := os.Open("data/List_of_attacks_Final.csv")
	if err != nil {
		log.Fatal(err)
	}
	defer inputFile.Close()

	outputFile, err := os.Create("data/List_of_attacks_Final-fixed.csv")
	if err != nil {
		log.Fatal(err)
	}
	defer outputFile.Close()

	var (
		inputReader  = csv.NewReader(inputFile)
		outputWriter = csv.NewWriter(outputFile)
		count        int
	)

	header := []string{
		"AttackNumber",
		"AttackNumberOriginal",
		"StartTime",
		"EndTime",
		"AttackDuration",
		"AttackPoints",
		"Adresses",
		"AttackName",
		"AttackType",
		"Intent",
		"ActualChange",
		"Notes",
	}

	// write header
	err = outputWriter.Write(header)
	if err != nil {
		log.Fatal(err)
	}

	records, err := inputReader.ReadAll()
	if err != nil {
		log.Fatal(err)
	}

	// iterate over all entries and ignore the additional infos at the end of the file
	for i, r := range records[:42] {

		// skip header
		if i == 0 {
			continue
		}

		// skip attacks without physical impact
		if r[3] == "No Physical Impact Attack" {
			fmt.Println("skipping attack number", i)
			continue
		}

		points := strings.ReplaceAll( // fix different notation
			strings.Trim(r[3], "\""), // remove " around the string
			"-",
			"",
		)
		var attackPoints []string
		if strings.Contains(points, ",") {
			attackPoints = strings.Split(points, ",")
		} else {
			attackPoints = strings.Split(points, ";")
		}

		addrs := []string{}
		num, err := strconv.Atoi(r[0])
		if err != nil {
			log.Fatal(err)
		}

		// lookup attack points to get ip addresses
		for _, point := range attackPoints {
			for _, stage := range stages {
				for _, device := range stage.devices {
					if device == point {
						addrs = stage.addrs
						break
					}
				}
			}

			if len(addrs) == 0 {
				fmt.Println("no addresses found for:", point)
			}
		}

		var attackType string
		for name, a := range attackTypes {
			for _, val := range a {
				if val == num {
					attackType = name
					break
				}
			}
		}

		// calculate duration
		start, err := time.Parse("2006/1/2 15:04:05", r[1])
		if err != nil {
			log.Fatal(count, err)
		}
		end, err := time.Parse("15:04:05", r[2])
		if err != nil {
			log.Fatal(count, err)
		}

		year, month, day := start.Date()
		end = time.Date(year, month, day, end.Hour(), end.Minute(), end.Second(), end.Nanosecond(), start.Location())
		duration := end.Sub(start).String()

		// fmt.Println(i, "start", start)
		// fmt.Println(i, "end", end)
		// fmt.Println(duration)

		count++
		err = outputWriter.Write([]string{
			strconv.Itoa(count),                 // Attack Number
			r[0],                                // Attack Number Original
			strconv.FormatInt(start.Unix(), 10), // Start Time
			strconv.FormatInt(end.Unix(), 10),   // End Time
			duration,                            // Attack Duration
			r[3],                                // Attack Points
			strings.Join(addrs, ","),            // Adresses
			r[5],                                // Attack Name
			attackType,                          // Attack Type
			r[7],                                // Intent
			r[6],                                // Actual Change
			r[8],                                // Notes
		})
		if err != nil {
			log.Fatal(err)
		}
	}

	outputWriter.Flush()
	err = outputWriter.Error()
	if err != nil {
		log.Fatal(err)
	}

	fmt.Println(count, "attacks written to", outputFile.Name())
	fmt.Println("header:", header)
}
