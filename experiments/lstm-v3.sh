#!/bin/bash

python3 train.py \
    -read "data/SWaT2015-Attack-Files-v0.2/train/*-labeled.csv" \
    -wrapLayerSize 5 \
    -dropoutLayer true \
    -coreLayerSize 10 \
    -epoch 1 \
    -zscoreUnixtime true \
    -lstm true \
    -features 16 \
    -drop modbus_value \
    -lstmBatchSize 100000 \
    -debug true

# EVAL
python3 score.py \
    -read "data/SWaT2015-Attack-Files-v0.2/eval/*-labeled.csv" \
    -wrapLayerSize 5 \
    -dropoutLayer true \
    -coreLayerSize 10 \
    -features 16 \
    -weights checkpoints/lstm-epoch-1-files-49-50-batch-200000-300000 \
    -drop modbus_value  \
    -lstm true  \
    -zscoreUnixtime true \
    -lstmBatchSize 100000 \
    -debug true