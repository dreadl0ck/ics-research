#!/bin/bash

# optimizer sgd , no dropout layer, 10 epochs, no zscoring of unixtime

python3 train.py \
    -read "data/SWaT2015-Attack-Files-v0.2/train/*-labeled.csv" \
    -wrapLayerSize 15 \
    -coreLayerSize 30 \
    -optimizer sgd \
    -epoch 10 \
    -lstm true \
    -features 16 \
    -drop modbus_value \
    -lstmBatchSize 100000

# EVAL
python3 score.py \
    -read "data/SWaT2015-Attack-Files-v0.2/eval/*-labeled.csv" \
    -wrapLayerSize 15 \
    -coreLayerSize 30 \
    -optimizer sgd \
    -features 16 \
    -weights checkpoints/lstm-epoch-10-files-49-50-batch-200000-300000 \
    -drop modbus_value  \
    -lstm true  \
    -lstmBatchSize 100000