#!/bin/bash

# corelayer: 50, wrap: 10, 10 epochs

python3 train.py \
    -read "data/SWaT2015-Attack-Files-v0.2/train/*-labeled.csv" \
    -wrapLayerSize 10 \
    -dropoutLayer true \
    -coreLayerSize 50 \
    -epoch 10 \
    -features 15 \
    -drop modbus_value

# EVAL
python3 score.py \
    -read "data/SWaT2015-Attack-Files-v0.2/eval/*-labeled.csv" \
    -wrapLayerSize 10 \
    -dropoutLayer true \
    -coreLayerSize 50 \
    -features 15 \
    -weights checkpoints/dn-epoch-10-files-49-50 \
    -drop modbus_value