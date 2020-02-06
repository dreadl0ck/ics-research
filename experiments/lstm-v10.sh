#!/bin/bash

python3 train.py \
    -read "$1" \
    -wrapLayerSize 8 \
    -dropoutLayer false \
    -relu false \
    -coreLayerSize 32 \
    -numCoreLayers 3 \
    -optimizer adam \
    -epoch 10 \
    -features 16 \
    -lstm true \
    -drop modbus_value

# EVAL
python3 score.py \
    -read "$2" \
    -wrapLayerSize 8 \
    -dropoutLayer false \
    -relu false \
    -coreLayerSize 32 \
    -numCoreLayers 3 \
    -optimizer adam \
    -features 16 \
    -lstm true \
    -drop modbus_value