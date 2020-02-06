# Experiments

> Training and Evaluation data do always differ!

The **<-** symbol denotes what has changed in comparision to the previous experiment!

## SINGLE FILE

- Single File training phase
- Single File eval phase

## MULTI

- Multi File training phase
- Multi File eval phase

## CONFIGURATIONS

multi example:

    python3 train.py \
    -read "data/SWaT2015-Attack-Files-v0.4/train/*-labeled.csv" \
    -wrapLayerSize 5 \
    -dropoutLayer true \
    -coreLayerSize 10 \
    -epoch 20 \
    -features 15 \
    -drop modbus_value \
    -optimizer sgd

    # EVAL
    python3 score.py \
        -read "data/SWaT2015-Attack-Files-v0.4/eval/*-labeled.csv" \
        -wrapLayerSize 5 \
        -dropoutLayer true \
        -coreLayerSize 10 \
        -optimizer sgd \
        -features 15 \
        -drop modbus_value

### Version 0

- 10 Epochs
- Optimizer: adam
- Activation: relu
- Dropout: False
- Wrap: 2
- Core: 4
- NumCore: 1
- BatchSize: 100.000

### Version 1

- 10 Epochs
- Optimizer: sgd <-
- Activation: relu
- Dropout: False
- Wrap: 2
- Core: 4
- NumCore: 1
- BatchSize: 100.000

### Version 2

- 10 Epochs
- Optimizer: adam <-
- Activation: relu
- Dropout: True <-
- Wrap: 2
- Core: 4
- NumCore: 1
- BatchSize: 100.000

### Version 3

- 10 Epochs
- Optimizer: sgd <-
- Activation: relu
- Dropout: True
- Wrap: 8 <-
- Core: 32 <-
- NumCore: 1
- BatchSize: 100.000

### Version 4

- 10 Epochs
- Optimizer: adam <-
- Activation: leakyrelu <-
- Dropout: True
- Wrap: 8
- Core: 32
- NumCore: 1
- BatchSize: 100.000

### Version 5

- 10 Epochs
- Optimizer: sgd <-
- Activation: relu <-
- Dropout: True
- Wrap: 16 <-
- Core: 64 <-
- NumCore: 1
- BatchSize: 100.000

### Version 6

- 10 Epochs
- Optimizer: adam <-
- Activation: relu
- Dropout: False <-
- Wrap: 16
- Core: 64
- NumCore: 1
- BatchSize: 100.000

### Version 7

- 10 Epochs
- Optimizer: sgd <-
- Activation: relu
- Dropout: False
- Wrap: 16
- Core: 64
- NumCore: 3 <-
- BatchSize: 100.000

### Version 8

- 20 Epochs
- Optimizer: adam <-
- Activation: relu
- Dropout: True <-
- Wrap: 16
- Core: 64
- NumCore: 3
- BatchSize: 100.000

### Version 9

- 30 Epochs
- Optimizer: sgd <-
- Activation: relu
- Dropout: True
- Wrap: 8
- Core: 32
- NumCore: 3 <-
- BatchSize: 100.000

### Version 10

- 30 Epochs
- Optimizer: adam
- Activation: leakyrelu <-
- Dropout: False <-
- Wrap: 8
- Core: 32
- NumCore: 3 <- 
- BatchSize: 100.000

