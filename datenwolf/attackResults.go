package main

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
