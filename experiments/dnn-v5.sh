#!/bin/bash

python3 train.py \
    -read "$1" \
    -wrapLayerSize 16 \
    -dropoutLayer true \
    -relu true \
    -coreLayerSize 64 \
    -numCoreLayers 1 \
    -optimizer sgd \
    -epoch 10 \
    -features 15 \
    -drop modbus_value

# EVAL
python3 score.py \
    -read "$2" \
    -wrapLayerSize 16 \
    -dropoutLayer true \
    -relu true \
    -coreLayerSize 64 \
    -numCoreLayers 1 \
    -optimizer sgd \
    -features 15 \
    -drop modbus_value