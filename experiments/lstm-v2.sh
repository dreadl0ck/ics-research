python3 train.py \
    -read "data/SWaT2015-Attack-Files-v0.2/2015-12-28_113021_98.log.part12_sorted-labeled.csv" \
    -wrapLayerSize 5 \
    -dropoutLayer true \
    -coreLayerSize 10 \
    -epoch 100 \
    -zscoreUnixtime true \
    -lstm true \
    -features 16 \
    -drop modbus_value \
    -lstmBatchSize 100
    #-debug true
    #-saveModel true

# EVAL
python3 score.py \
    -read "data/SWaT2015-Attack-Files-v0.2/2015-12-28_113021_98.log.part13_sorted-labeled.csv" \
    -wrapLayerSize 5 \
    -dropoutLayer true \
    -coreLayerSize 10 \
    -features 16 \
    -weights checkpoints/lstm-epoch-100-files-0-1-batch-499900-500000 \
    -drop modbus_value  \
    -lstm true  \
    -zscoreUnixtime true \
    -lstmBatchSize 100 \
    -debug true