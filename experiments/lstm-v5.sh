#!/bin/bash

# corelayer: 30, wrap: 15, 10 epochs

python3 train.py \
    -read "data/SWaT2015-Attack-Files-v0.2/train/*-labeled.csv" \
    -wrapLayerSize 15 \
    -dropoutLayer true \
    -coreLayerSize 30 \
    -epoch 10 \
    -zscoreUnixtime true \
    -lstm true \
    -features 16 \
    -drop modbus_value \
    -lstmBatchSize 100000

# EVAL
python3 score.py \
    -read "data/SWaT2015-Attack-Files-v0.2/eval/*-labeled.csv" \
    -wrapLayerSize 15 \
    -dropoutLayer true \
    -coreLayerSize 30 \
    -features 16 \
    -weights checkpoints/lstm-epoch-10-files-49-50-batch-200000-300000 \
    -drop modbus_value  \
    -lstm true  \
    -zscoreUnixtime true \
    -lstmBatchSize 100000