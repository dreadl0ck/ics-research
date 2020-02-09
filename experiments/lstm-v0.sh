#!/bin/bash -e

python3 train.py \
    -read "$1" \
    -wrapLayerSize 2 \
    -dropoutLayer false \
    -relu true \
    -coreLayerSize 4 \
    -numCoreLayers 1 \
    -optimizer adam \
    -epoch 3 \
    -features 107 \
    -lstm true \
    -debug true \
    -drop modbus_value

# EVAL
python3 score.py \
    -read "$2" \
    -wrapLayerSize 2 \
    -dropoutLayer false \
    -relu true \
    -coreLayerSize 4 \
    -numCoreLayers 1 \
    -optimizer adam \
    -lstm true \
    -features 107 \
    -debug true \
    -drop modbus_value
