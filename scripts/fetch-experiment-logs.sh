#!/bin/bash

echo "[INFO] downloading logs from bastia"
mkdir -p experiment-logs/bastia
scp -P 9876 user@someserver.net:/ics/ics-research/experiment-logs/*.log experiment-logs/bastia

echo "[INFO] downloading logs from brussels"
mkdir -p experiment-logs/brussels
scp -P 9876 user@someserver.net:/home/user/ics-research/experiment-logs/*.log experiment-logs/brussels

