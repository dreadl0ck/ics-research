#!/bin/bash

red=$'\e[1;31m'
grn=$'\e[1;32m'
yel=$'\e[1;33m'
blu=$'\e[1;34m'
mag=$'\e[1;35m'
cyn=$'\e[1;36m'
end=$'\e[0m'

total=0
current=0

function log() {
    echo -e "${red} [ $current / $total ] > ${end} $@"
}

for f in *-logs
do
	((total++))
done

for f in *-logs
do
	((current++))
	res=$(cat "$f/fast.log" | grep -v "Generic Protocol Command Decode]")
	if [[ "$res" != "" ]]
	then
		log "$f"
		echo "$res"
	fi
done
