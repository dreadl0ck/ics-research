package main

import "strconv"

const prec = 10

func minMax(value float64, sum columnSummary) string {
	return strconv.FormatFloat((value-sum.Min)/(sum.Max-sum.Min), 'f', prec, 64)
}

func zScore(i float64, sum columnSummary) string {
	return strconv.FormatFloat((i-sum.Mean)/sum.Std, 'f', prec, 64)
}

func getIndex(arr []string, val string) float64 {

	for index, v := range arr {
		if v == val {
			return float64(index)
		}
	}

	return float64(0)
}
