#!/bin/bash

# SGD optimizer, corelayer: 10, wrap: 5, 10 epochs

python3 train.py \
    -read "data/SWaT2015-Attack-Files-v0.2/train/*-labeled.csv" \
    -wrapLayerSize 5 \
    -dropoutLayer true \
    -coreLayerSize 10 \
    -epoch 10 \
    -features 15 \
    -drop modbus_value \
    -optimizer sgd

# EVAL
python3 score.py \
    -read "data/SWaT2015-Attack-Files-v0.2/eval/*-labeled.csv" \
    -wrapLayerSize 5 \
    -dropoutLayer true \
    -coreLayerSize 10 \
    -optimizer sgd \
    -features 15 \
    -weights checkpoints/dn-epoch-10-files-49-50 \
    -drop modbus_value
