#!/usr/bin/python3

# Run LSTM, locally:
# $ ./readcsv.py -read data/TCP_labeled.csv -dimensionality 22 -class_amount 2 -sample 0.5 -lstm true
# on server, 2019 SWaT dataset:
# $ ./readcsv.py -read */TCP_labeled.csv -dimensionality 22 -class_amount 2 -sample 0.5 -lstm true
# on server, 2015 SWaT dataset:
# $ ./readcsv.py -read */*_labeled.csv -dimensionality XX -class_amount 2 -sample 0.5 -lstm true

from tfUtils import * 
from glob import glob
import argparse

import pandas as pd

from sklearn.model_selection import train_test_split

import keras
from keras.models import Sequential
from keras.layers.core import Dense, Activation
from keras.callbacks import EarlyStopping
from termcolor import colored

monitor = EarlyStopping(
    monitor='val_loss', 
    min_delta=1e-3, 
    patience=5, 
    verbose=1, 
    mode='auto'
)

# TODO hardcoded these are the labeltypes that can be found in the dataset
labeltypes = ["normal", "Single Stage Single Point Attacks", "Single Stage Multi Point Attacks", "Multi Stage Single Point Attacks", "Multi Stage Multi Point Attacks"]
#labeltypes = ["Normal", "Attack"]

#instantiate the parser
def train_dnn(df):

    print("[INFO] breaking into predictors and prediction...")
    # Break into X (predictors) & y (prediction)
    x, y = to_xy(df, arguments.result_column, labeltypes)

    print("[INFO] creating train/test split:", arguments.test_size)

    # Create a test/train split.
    # by default, 25% of data is used for testing
    # it can be configured using the test_size commandline flag
    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=arguments.test_size,
        random_state=42,
        shuffle=arguments.shuffle
    )

    if arguments.debug:
        print("--------SHAPES--------")
        print("x_train.shape", x_train.shape)
        print("x_test.shape", x_test.shape)
        print("y_train.shape", y_train.shape)
        print("y_test.shape", y_test.shape)

    if arguments.lstm:

        print(colored("[INFO] using LSTM layers", 'yellow'))
        x_train = x_train.reshape(-1, x_train.shape[0], x.shape[1])
        x_test = x_test.reshape(-1, x_test.shape[0], x.shape[1])
        y_train = y_train.reshape(-1, y_train.shape[0], y.shape[1])
        y_test = y_test.reshape(-1, y_test.shape[0], y.shape[1])

        if arguments.debug:
            print("--------RESHAPED--------")
            print("x_train.shape", x_train.shape)
            print("x_test.shape", x_test.shape)
            print("y_train.shape", y_train.shape)
            print("y_test.shape", y_test.shape)

    # TODO: using a timestep size of 1 and feeding numRows batches should also work
    #x_train = np.reshape(x_train, (x_train.shape[0], 1, x_train.shape[1]))
    #x_test = np.reshape(x_test, (x_test.shape[0], 1, x_test.shape[1]))

    print("[INFO] fitting model")
    model.fit(
        x_train,
        y_train,
        validation_data=(x_test, y_test),
        callbacks=[monitor],
        verbose=2,
        epochs=1,
        batch_size=32
    )

    # TODO: mkdir checkpoints

    print("[INFO] saving weights")
    model.save_weights('./checkpoints/epoch-{}-files-{}-{}'.format(1, i, i+batch_size))

def readCSV(f):
    print("[INFO] reading file", f)
    return pd.read_csv(f, delimiter=',', engine='c', encoding="utf-8-sig")

# instantiate the parser
parser = argparse.ArgumentParser(description='NETCAP compatible implementation of Network Anomaly Detection with a Deep Neural Network and TensorFlow')

# add commandline flags
parser.add_argument('-read', required=True, type=str, help='Regex to find all labeled input CSV file to read from (required)')
parser.add_argument('-drop', type=str, help='optionally drop specified columns, supply multiple with comma')
parser.add_argument('-sample', type=float, nargs='?', help='optionally sample only a fraction of records')
parser.add_argument('-dropna', default=False, action='store_true', help='drop rows with missing values')
parser.add_argument('-test_size', type=float, default=0.5, help='specify size of the test data in percent (default: 0.25)')
parser.add_argument('-loss', type=str, default='categorical_crossentropy', help='set function (default: categorical_crossentropy)')
parser.add_argument('-optimizer', type=str, default='adam', help='set optimizer (default: adam)')
parser.add_argument('-result_column', type=str, default='Normal/Attack', help='set name of the column with the prediction')
parser.add_argument('-dimensionality', type=int, required=True, help='The amount of columns in the csv')
#parser.add_argument('-class_amount', type=int, default=2, help='The amount of classes e.g. normal, attack1, attack3 is 3')
parser.add_argument('-batch_size', type=int, default=1, help='The amount of files to be read in. (default: 1)')
parser.add_argument('-epochs', type=int, default=1, help='The amount of epochs. (default: 1)')
parser.add_argument('-numCoreLayers', type=int, default=1, help='set number of core layers to use')
parser.add_argument('-shuffle', default=False, help='shuffle data before feeding it to the DNN')
parser.add_argument('-dropoutLayer', default=False, help='insert a dropout layer at the end')
parser.add_argument('-coreLayerSize', type=int, default=4, help='size of an DNN core layer')
parser.add_argument('-wrapLayerSize', type=int, default=2, help='size of the first and last DNN layer')
parser.add_argument('-lstm', default=False, help='use a LSTM network')
parser.add_argument('-lstmBatchSize', type=int, default=10000, help='LSTM network input number of rows')
parser.add_argument('-debug', default=False, help='debug mode on off')

# parse commandline arguments
arguments = parser.parse_args()
if arguments.read is None:
    print("[INFO] need an input file. use the -r flag")
    exit(1)

# get all files
files = glob(arguments.read)
files.sort()

# set batch size
batch_size = arguments.batch_size

# create models
model = create_dnn(
    arguments.dimensionality, 
    len(labeltypes), 
    arguments.loss, 
    arguments.optimizer, 
    arguments.lstm, 
    arguments.numCoreLayers,
    arguments.coreLayerSize,
    arguments.dropoutLayer,
    arguments.lstmBatchSize,
    arguments.wrapLayerSize
)
print("[INFO] created DNN")

leftover = None
for epoch in range(arguments.epochs):

    print(colored("[INFO] epoch {}/{}".format(epoch, arguments.epochs), 'yellow'))
    for i in range(0, len(files), batch_size):

        print(colored("[INFO] loading file {}-{} on epoch {}/{}".format(i, i+batch_size, epoch, arguments.epochs), 'yellow'))
        df_from_each_file = [readCSV(f) for f in files[i:(i+batch_size)]]

        if leftover and len(leftover.index):
            df_from_each_file.insert(0, leftover)

        print("[INFO] concatenate the files")
        df = pd.concat(df_from_each_file, ignore_index=True)

        print("[INFO] process dataset, shape:", df.shape)
        process_dataset(df, arguments.sample, arguments.drop, arguments.lstm)

        print("[INFO] analyze dataset:", df.shape)
        analyze(df)

        print("[INFO] encoding dataset:", df.shape)
        encode_columns(df, arguments.result_column, arguments.lstm, arguments.debug)
        print("[INFO] AFTER encoding dataset:", df.shape)

        if arguments.lstm:
            for i in range(0, df.shape[0], arguments.lstmBatchSize):

                dfCopy = df[i:i+arguments.lstmBatchSize]

                # skip leftover that does not reach batch size
                if len(dfCopy.index) != arguments.lstmBatchSize:
                    leftover = dfCopy
                    continue

                train_dnn(dfCopy)
                leftover = None
        else:
            train_dnn(df)
