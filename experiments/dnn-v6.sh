#!/bin/bash

python3 train.py \
    -read "$1" \
    -wrapLayerSize 16 \
    -dropoutLayer false \
    -relu true \
    -coreLayerSize 64 \
    -numCoreLayers 1 \
    -optimizer adam \
    -epoch 3 \
    -features 105 \
    -drop modbus_value

# EVAL
python3 score.py \
    -read "$2" \
    -wrapLayerSize 16 \
    -dropoutLayer false \
    -relu true \
    -coreLayerSize 64 \
    -numCoreLayers 1 \
    -optimizer adam \
    -features 105 \
    -drop modbus_value