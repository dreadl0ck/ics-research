package main

type correction struct {
	old string
	new string
}

func newCorrection(old, new string) correction {
	return correction{
		old: old,
		new: new,
	}
}

// columns mapped to corrections
var cmap = map[string][]correction{
	"proxy_src_ip": []correction{
		newCorrection("192.16:.1.10", "192.168.1.10"),
	},
	"type": []correction{
		newCorrection("loe", "log"),
	},
	"Modbus_Function_Description": []correction{
		newCorrection("Read Tag Service - Responqe", "Read Tag Service - Response"),
	},
}

var simpleCorrect = map[string]string{
	"192.16:.1.10":                "192.168.1.10",
	"loe":                         "log",
	"Read Tag Service - Responqe": "Read Tag Service - Response",
}
