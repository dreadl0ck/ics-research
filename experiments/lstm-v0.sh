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
    -features 16 \
    -lstm true \
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
    -features 16 \
    -drop modbus_value
