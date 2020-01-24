#!/usr/bin/env python -u
# coding: utf-8
# python buffers stdout when it's not a terminal, -u flag unbuffers
# used to get output live when using tee

#################################################################################################################################################################
#                                                                                                                                                               #
# This program is based on code from Jeff Heaton's Washington University (in St. Louis) Course T81-558: Applications of Deep Neural Networks.                   #
# It is licensed under the Apache License 2.0.                                                                                                                  #
# It was modified by Philipp Mieden <dreadl0ck [at] protonmail [dot] ch> for the NETCAP research project.                                                       #
# It was modfied by Rutger Beltman, the deep neural network code was replaced by a Code for a support vector machine.#
# usage:                                                                                                                                                              #                   #
# $ python3 tf-dnn.py -read data.csv
# help:
# $ python3 tf-dnn.py -h
#################################################################################################################################################################

import pandas as pd
import io
import requests
import os

from sklearn import svm
from sklearn import metrics

import numpy as np
import argparse
import shutil
import base64
import time
import sys

from termcolor import colored
from sklearn.model_selection import train_test_split
from sklearn import metrics
from sklearn import preprocessing
from scipy.stats import zscore

ENCODING = 'utf-8'

##
## UTILS
##

## Encoding Utils

def encode_string(df, name):
    """
    Encode string decides which method for encoding strings will be called.
    """
    if arguments.string_index:
        encode_text_index(df, col)
    if arguments.string_dummy:
        encode_text_dummy(df, col)

def encode_text_dummy(df, name):
    """
    Encodes text values to dummy variables(i.e. [1,0,0],[0,1,0],[0,0,1] for red,green,blue).
    """
    print(colored("encode_text_dummy " + name, "yellow"))
    dummies = pd.get_dummies(df[name])
    for x in dummies.columns:
        dummy_name = "{}-{}".format(name, x)
        df[dummy_name] = dummies[x]
    df.drop(name, axis=1, inplace=True)


def encode_text_single_dummy(df, name, target_values):
    """
    Encodes text values to a single dummy variable.  The new columns (which do not replace the old) will have a 1
    at every location where the original column (name) matches each of the target_values.  One column is added for
    each target value.
    """
    for tv in target_values:
        l = list(df[name].astype(str))
        l = [1 if str(x) == str(tv) else 0 for x in l]
        name2 = "{}-{}".format(name, tv)
        df[name2] = l

def encode_text_index(df, name):
    """
    Encodes text values to indexes(i.e. [1],[2],[3] for red,green,blue).
    """
    # replace missing values (NaN) with an empty string
    df[name].fillna('',inplace=True)
    print(colored("encode_text_index " + name, "yellow"))
    le = preprocessing.LabelEncoder()
    df[name] = le.fit_transform(df[name])
    return le.classes_

def encode_outputtype(df, name):
    """
    Creates a boolean Series and casting to int converts True and False to 1 and 0 respectively.
    """
    print(colored("encode_outputtype " + name, "yellow"))
    df[name] = 1 if df[name] == "normal" else 0 

def encode_bool(df, name):
    """
    Creates a boolean Series and casting to int converts True and False to 1 and 0 respectively.
    """
    print(colored("encode_bool " + name, "yellow"))
    df[name] = df[name].astype(int)

def encode_numeric_zscore(df, name, mean=None, sd=None):
    """
    Encodes a numeric column as zscores.
    """
    # replace missing values (NaN) with a 0
    df[name].fillna(0,inplace=True)
    print(colored("encode_numeric_zscore " + name, "yellow"))
    if mean is None:
        mean = df[name].mean()

    if sd is None:
        sd = df[name].std()

    df[name] = (df[name] - mean) / sd

def to_xy(df, target):
    """
    Converts a pandas dataframe to the x,y inputs that TensorFlow needs.
    """
    result = []
    for x in df.columns:
        if x != target:
            result.append(x)
    # find out the type of the target column.  Is it really this hard? :(
    target_type = df[target].dtypes
    target_type = target_type[0] if hasattr(target_type, '__iter__') else target_type
    # Encode to int for classification, float otherwise. TensorFlow likes 32 bits.
    if target_type in (np.int64, np.int32):
        # Classification
        dummies = pd.get_dummies(df[target])

        # as_matrix is deprecated
        #return df.as_matrix(result).astype(np.float32), dummies.as_matrix().astype(np.float32)
        return df[result].values.astype(np.float32), dummies.values.astype(np.float32)
    else:
        # Regression
        # as_matrix is deprecated
        #return df.as_matrix(result).astype(np.float32), df.as_matrix([target]).astype(np.float32)
        return df[result].values.astype(np.float32), df[target].values.astype(np.float32)

## TODO: add flags for these

def missing_median(df, name):
    """
    Converts all missing values in the specified column to the median.
    """
    med = df[name].median()
    df[name] = df[name].fillna(med)


def missing_default(df, name, default_value):
    """
    Converts all missing values in the specified column to the default.
    """
    df[name] = df[name].fillna(default_value)

def hms_string(sec_elapsed):
    """
    Returns a nicely formatted time string.
    eg: 1h 15m 14s
           12m 11s
                6s
    """
    h = int(sec_elapsed / (60 * 60))
    m = int((sec_elapsed % (60 * 60)) / 60)
    s = sec_elapsed % 60
    if h == 0 and m == 0:
        return "{:2.0f}s".format(s)
    elif h == 0:
        return "{}m {:2.0f}s".format(m, s)
    else:
        return "{}h {}m {:2.0f}s".format(h, m, s)

def drop_col(name, df):
    """
    Drops a column if it exists in the dataset.
    """
    if name in df.columns:
        print(colored("dropping column: " + name, "yellow"))
        df.drop(columns=[name],axis=1, inplace=True)

## File Size Utils

def convert_bytes(num):
    """
    Converts bytes to human readable format.
    """
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0


def file_size(file_path):
    """
    Returns size of a file in bytes.
    """
    if os.path.isfile(file_path):
        file_info = os.stat(file_path) 
        return convert_bytes(file_info.st_size)
    else:
        print("not a file:", file_path)


##
## MAIN
##

start_time = time.time()

## Commandline Arguments
##

print("[INFO] sys.argv:", sys.argv)

# Instantiate the parser
parser = argparse.ArgumentParser(description='NETCAP compatible implementation of Network Anomaly Detection with a Deep Neural Network and TensorFlow')

# add commandline flags
parser.add_argument('-read', required=True, type=str, help='Labeled input CSV file to read from (required)')
parser.add_argument('-drop', type=str, help='optionally drop specified columns, supply multiple with comma')
parser.add_argument('-sample', type=float, nargs='?', help='optionally sample only a fraction of records')
parser.add_argument('-dropna', default=False, action='store_true', help='drop rows with missing values')
parser.add_argument('-string_dummy', default=False, action='store_true', help='encode strings as dummy variables')
parser.add_argument('-string_index', default=True, action='store_true', help='encode strings as indices (default)')
parser.add_argument('-test_size', type=float, default=0.25, help='specify size of the test data in percent (default: 0.25)')
parser.add_argument('-loss', type=str, default='categorical_crossentropy', help='set function (default: categorical_crossentropy)')
parser.add_argument('-optimizer', type=str, default='adam', help='set optimizer (default: adam)')
parser.add_argument('-result_column', type=str, default='Normal/Attack', help='set name of the column with the prediction')

## parse commandline arguments
arguments = parser.parse_args()
if arguments.read == None:
    print("[INFO] need an input file. use the -r flag")
    exit(1)

# there can only be one option selected
if arguments.string_dummy:
    arguments.string_index = False

print("[INFO] arguments:", arguments)
path = arguments.read

## Read in Dataset
##

print(colored("reading file " + path, 'yellow'))
print(colored("Input File Size: " + file_size(path), 'red'))

# read input file
df = pd.read_csv(
    path, 
    delimiter=',', 
    engine='c', 
    encoding="utf-8-sig",
)

print(colored("Read {} rows.".format(len(df)), "yellow"))

if arguments.sample != None:
    if arguments.sample >= 1.0:
        parser.error("invalid sample rate")
    
    if arguments.sample <= 0:
        parser.error("invalid sample rate")
    
    print("[INFO] sampling", arguments.sample)
    df = df.sample(frac=arguments.sample, replace=False) # Uncomment this line to sample only 50% of the dataset

# Always drop columns that are unique for every record
drop_col('UID', df)
drop_col('SessionID', df)
drop_col('date', df)
drop_col('time', df)

# Drop additionally specified columns from the dataset
if arguments.drop != None:
    for col in arguments.drop.split(","):
        drop_col(col, df)

print("[INFO] columns:", df.columns)

# Drop NA's (rows with missing numeric values) prior to encoding if desired
if arguments.dropna:
    print("[INFO] dropping rows with missing numeric values, number of rows before:", len(df.index))
    df.dropna(inplace=True,axis=1)
    print("[INFO] number of rows after dropping:", len(df.index))

##
## ANALYZE DATASET
##

# The following script can be used to give a high level overview of how a dataset appears.

def expand_categories(values):
    result = []
    s = values.value_counts()
    t = float(len(values))
    for v in s.index:
        result.append("{}:{}%".format(v,round(100*(s[v]/t),5)))
    return "[{}]".format(",".join(result))
        
def analyze(filename):
    print()
    print("[INFO] Analyzing: {}".format(filename))
    df = pd.read_csv(filename,encoding=ENCODING)
    cols = df.columns.values
    total = float(len(df))

    print("[INFO] {} rows".format(int(total)))
    for col in cols:
        uniques = df[col].unique()
        unique_count = len(uniques)
        if unique_count>100:
            print("[INFO] ** {}:{} ({}%)".format(col,unique_count,round((unique_count/total)*100,5)))
        else:
            print("[INFO] ** {}:{}".format(col,expand_categories(df[col])))
            expand_categories(df[col])


# run analysis
analyze(path)

##
## ENCODERS
##

# Encode the feature vector
# Encode every row in the database.
# This takes a while depending on the size of the dataset

## Encoder Dictionaries

encoders = {
    # Flow / Connection
    'TimestampFirst'   : encode_numeric_zscore,
    'LinkProto'        : encode_string,
    'NetworkProto'     : encode_string,
    'TransportProto'   : encode_string,
    'ApplicationProto' : encode_string,
    'SrcMAC'           : encode_string,
    'DstMAC'           : encode_string,
    'SrcIP'            : encode_string,
    'SrcPort'          : encode_numeric_zscore,
    'DstIP'            : encode_string,
    'DstPort'          : encode_numeric_zscore,
    'Size'             : encode_numeric_zscore,
    'AppPayloadSize'   : encode_numeric_zscore,
    'NumPackets'       : encode_numeric_zscore,
    'UID'              : encode_string,
    'Duration'         : encode_numeric_zscore,
    'TimestampLast'    : encode_numeric_zscore,
    
    # UDP specific fields
    'Length'           : encode_numeric_zscore,
    'Checksum'         : encode_numeric_zscore,
    'PayloadEntropy'   : encode_numeric_zscore,
    'PayloadSize'      : encode_numeric_zscore,
    'Timestamp'        : encode_numeric_zscore,
    
    # TCP specific fields
    'SeqNum'           : encode_numeric_zscore,
    'AckNum'           : encode_numeric_zscore,
    'DataOffset'       : encode_numeric_zscore,
    'FIN'              : encode_bool,
    'SYN'              : encode_bool,
    'RST'              : encode_bool,
    'PSH'              : encode_bool,
    'ACK'              : encode_bool,
    'URG'              : encode_bool,
    'ECE'              : encode_bool,
    'CWR'              : encode_bool,
    'NS'               : encode_bool,
    'Window'           : encode_numeric_zscore,
    'Urgent'           : encode_numeric_zscore,
    'Padding'          : encode_numeric_zscore,
    'Options'          : encode_string,
    
    # ARP
    'AddrType'          : encode_numeric_zscore,
    'Protocol'          : encode_numeric_zscore,
    'HwAddressSize'     : encode_numeric_zscore,
    'ProtAddressSize'   : encode_numeric_zscore,
    'Operation'         : encode_numeric_zscore,
    'SrcHwAddress'      : encode_string,
    'SrcProtAddress'    : encode_string,
    'DstHwAddress'      : encode_string,
    'DstProtAddress'    : encode_string,
    
    # Layer Flows
    'Proto'                : encode_string,
    
    # NTP
    'LeapIndicator'        : encode_numeric_zscore,     #int32 
    'Version'              : encode_numeric_zscore,     #int32 
    'Mode'                 : encode_numeric_zscore,     #int32 
    'Stratum'              : encode_numeric_zscore,     #int32 
    'Poll'                 : encode_numeric_zscore,     #int32 
    'Precision'            : encode_numeric_zscore,     #int32 
    'RootDelay'            : encode_numeric_zscore,     #uint32
    'RootDispersion'       : encode_numeric_zscore,     #uint32
    'ReferenceID'          : encode_numeric_zscore,     #uint32
    'ReferenceTimestamp'   : encode_numeric_zscore,     #uint64
    'OriginTimestamp'      : encode_numeric_zscore,     #uint64
    'ReceiveTimestamp'     : encode_numeric_zscore,     #uint64
    'TransmitTimestamp'    : encode_numeric_zscore,     #uint64
    'ExtensionBytes'       : encode_string,         #[]byte

    # Ethernet
    'EthernetType'        : encode_numeric_zscore,     #int32 

    # IPv4
    'IHL'                : encode_numeric_zscore,  # int32
    'TOS'                : encode_numeric_zscore,  # int32
    'Id'                 : encode_numeric_zscore,  # int32
    'Flags'              : encode_numeric_zscore,  # int32
    'FragOffset'         : encode_numeric_zscore,  # int32
    'TTL'                : encode_numeric_zscore,  # int32

    # IPv6
    'TrafficClass'     : encode_numeric_zscore,  # int32
    'FlowLabel'        : encode_numeric_zscore,  # uint32       
    'Length'           : encode_numeric_zscore,  # int32        
    'NextHeader'       : encode_numeric_zscore,  # int32        
    'HopLimit'         : encode_numeric_zscore,  # int32        
    'SrcIP'            : encode_string,      # string       
    'DstIP'            : encode_string,      # string       
    'PayloadEntropy'   : encode_numeric_zscore,  # float64      
    'PayloadSize'      : encode_numeric_zscore,  # int32        
    'HopByHop'         : encode_string,      # *IPv6HopByHop

    # HTTP
    'Method'           : encode_string,
    'Host'             : encode_string,
    'UserAgent'        : encode_string,
    'Referer'          : encode_string,
    "ReqCookies"       : encode_string,
    'ReqContentLength' : encode_numeric_zscore,
    'URL'              : encode_string,
    'ResContentLength' : encode_numeric_zscore,
    'ContentType'      : encode_string,
    'StatusCode'       : encode_numeric_zscore,

    # DNS
    'ID'           : encode_numeric_zscore, # int32
    'QR'           : encode_bool, # bool 
    'OpCode'       : encode_numeric_zscore, # int32
    'AA'           : encode_bool, # bool 
    'TC'           : encode_bool, # bool 
    'RD'           : encode_bool, # bool 
    'RA'           : encode_bool, # bool 
    'Z'            : encode_numeric_zscore, # int32
    'ResponseCode' : encode_numeric_zscore, # int32
    'QDCount'      : encode_numeric_zscore, # int32
    'ANCount'      : encode_numeric_zscore, # int32
    'NSCount'      : encode_numeric_zscore, # int32
    'ARCount'      : encode_numeric_zscore, # int32
    'Questions'    : encode_string,
    'Answers'      : encode_string,
    'Authorities'  : encode_string,
    'Additionals'  : encode_string,

    'Type'               : encode_numeric_zscore, # int32   
    'MessageLen'         : encode_numeric_zscore, # int32   
    'HandshakeType'      : encode_numeric_zscore, # int32   
    'HandshakeLen'       : encode_numeric_zscore, # uint32  
    'HandshakeVersion'   : encode_numeric_zscore, # int32   
    'Random'             : encode_string, # string
    'SessionIDLen'       : encode_numeric_zscore,  # uint32  
    'SessionID'          : encode_string, # string, will be dropped 
    'CipherSuiteLen'     : encode_numeric_zscore,  # int32   
    'ExtensionLen'       : encode_numeric_zscore,  # int32   
    'SNI'                : encode_string, # string  
    'OSCP'               : encode_bool,   # bool    
    'CipherSuites'       : encode_string, # string 
    'CompressMethods'    : encode_string, # string 
    'SignatureAlgs'      : encode_string, # string 
    'SupportedGroups'    : encode_string, # string 
    'SupportedPoints'    : encode_string, # string 
    'ALPNs'              : encode_string, # string
    'Ja3'                : encode_string, # string

    #labeled dataset swat specific
    'num'                             : encode_string,
    'date'                            : encode_string,
    'time'                            : encode_string,
    'orig'                            : encode_string,
    'type'                            : encode_string,
    'i/f_name'                        : encode_string,
    'i/f_dir'                         : encode_string,
    'src'                             : encode_string,
    'dst'                             : encode_string,
    'proto'                           : encode_string,
    'appi_name'                       : encode_string,
    'proxy_src_ip'                    : encode_string,
    'Modbus_Function_Code'            : encode_numeric_zscore,
    'Modbus_Function_Description'     : encode_string,
    'Modbus_Transaction_ID'           : encode_numeric_zscore,
    'SCADA_Tag'                       : encode_string,
    'Modbus_Value'                    : encode_string,
    'service'                         : encode_numeric_zscore,
    's_port'                          : encode_numeric_zscore,
    'Tag'                             : encode_numeric_zscore,
    'Normal/Attack'                   : encode_outputtype,

}

import datetime

# Encode all values by looking up each column name and picking the configured encoding method
for col in df.columns:
    colName = col.strip()
    if colName != arguments.result_column:
        if colName in encoders:
            encoders[colName](df, col)
        else:
            #print("[INFO] could not locate", colName, "in encoder dict. Defaulting to encode_numeric_zscore")
            encode_numeric_zscore(df, col)
 
# Encode result as text index
print("[INFO] result_column:", arguments.result_column)
outcomes = encode_text_index(df, arguments.result_column)

# Print number of classes
num_classes = len(outcomes)
print("[INFO] num_classes", num_classes)

# Remove incomplete records after encoding
df.dropna(inplace=True,axis=1)


print("[INFO] breaking into predictors and prediction...")

# Break into X (predictors) & y (prediction)
x, y = to_xy(df, arguments.result_column)
print("[INFO] creating train/test split")

# Create a test/train split.
# by default, 25% of data is used for testing
# it can be configured using the test_size commandline flag
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=arguments.test_size, random_state=42)

# Create the SVM classifer.
print("[INFO] y_train.shape", y_train.shape)
print("[INFO] x_train.shape", x_train.shape)
clf = svm.SVC()
print("[INFO] fitting svm")
clf.fit(x_train,y_train)
print("[INFO] Testing SVM")
y_predict = clf.predict(x_test)


print("[INFO] statistics")
print("Accuracy:",metrics.accuracy_score(y_test[:,1], y_predict))
print("Recall",metrics.recall_score(y_test[:,1], y_predict))
print("precision",metrics.precision_score(y_test[:,1], y_predict))

confusion_matrix = metrics.confusion_matrix(y_test[:,1], y_predict)
print("true  positives:", confusion_matrix[1,1])
print("true  negatives:", confusion_matrix[0,0])
print("false positives:", confusion_matrix[1,0])
print("false negatives:", confusion_matrix[1,0])
