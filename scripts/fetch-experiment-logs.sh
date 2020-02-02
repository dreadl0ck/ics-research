#!/bin/bash

echo "[INFO] downloading logs from ***REMOVED***"
mkdir -p experiment-logs/***REMOVED***
scp -P 9876 ***REMOVED***@***REMOVED***:/home/***REMOVED***/ics-research/experiment-logs/*.log experiment-logs/***REMOVED***

echo "[INFO] downloading logs from brussels"
mkdir -p experiment-logs/brussels
scp -P 9876 ***REMOVED***@***REMOVED***:/home/***REMOVED***/ics-research/experiment-logs/*.log experiment-logs/brussels

