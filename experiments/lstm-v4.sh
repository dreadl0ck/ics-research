#!/bin/bash

python3 train.py \
    -read "$1" \
    -wrapLayerSize 8 \
    -dropoutLayer true \
    -relu false \
    -coreLayerSize 32 \
    -numCoreLayers 1 \
    -optimizer adam \
    -epoch 3 \
    -features 107 \
    -lstm true \
    -drop modbus_value

# EVAL
python3 score.py \
    -read "$2" \
    -wrapLayerSize 8 \
    -dropoutLayer true \
    -relu false \
    -coreLayerSize 32 \
    -numCoreLayers 1 \
    -optimizer adam \
    -features 107 \
    -lstm true \
    -drop modbus_value