package main

/*
 * Utils
 */

// ClearLine clears the current line of the terminal
func clearLine() {
	print("\033[2K\r")
}
