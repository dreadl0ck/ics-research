package main

import "strconv"

/*
 * Utils
 */

// ClearLine clears the current line of the terminal
func clearLine() {
	print("\033[2K\r")
}

func getIndex(arr []string, val string) string {

	for index, v := range arr {
		if v == val {
			return strconv.Itoa(index)
		}
	}

	return "not-found"
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
