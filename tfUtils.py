from keras.models import Sequential
from keras.layers.core import Dense, Activation 
import keras
import numpy as np
import pandas as pd
import os
from termcolor import colored
from sklearn import preprocessing
from keras import layers
from keras.layers import Dropout

def encode_string(df, name):
    """
    Encodes text values to indexes(i.e. [1],[2],[3] for red,green,blue).
    """
    # replace missing values (NaN) with an empty string
    df[name].fillna('', inplace=True)
    print(colored("encode_string " + name, "yellow"))
    le = preprocessing.LabelEncoder()
    df[name] = le.fit_transform(df[name])
    return le.classes_


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
    
    # replace missing values (NaN) with a 0
    df[name].fillna(0,inplace=True)


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

    # SWaT 2015 Network CSVs
    "num"                          : encode_numeric_zscore,
    "date"                         : encode_string,
    "time"                         : encode_string,
    "orig"                         : encode_string,
    "type"                         : encode_string,
    "i/f_name"                     : encode_string,
    "i/f_dir"                      : encode_string,
    "src"                          : encode_string,
    "dst"                          : encode_string,
    "proto"                        : encode_string,
    "appi_name"                    : encode_string,
    "proxy_src_ip"                 : encode_string,
    "Modbus_Function_Code"         : encode_numeric_zscore,
    "Modbus_Function_Description"  : encode_string,
    "Modbus_Transaction_ID"        : encode_numeric_zscore,
    "SCADA_Tag"                    : encode_string,
    "Modbus_Value"                 : encode_string,
    "service"                      : encode_numeric_zscore,
    "s_port"                       : encode_numeric_zscore,
    "Tag"                          : encode_numeric_zscore,
}


def to_xy(df, target, labeltypes):
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
 
    
    values = df[target].values
    y_vector = np.zeros((values.shape[0],len(labeltypes)))

    # loop through all of the labeltypes and flag the columns that contain the label type
    for i,j in enumerate(labeltypes):

        indices = np.where(values == j)
        y_vector[indices,i] = 1
    return df[result].values.astype(np.float32), y_vector

    # Encode to int for classification, float otherwise. TensorFlow likes 32 bits.
    # if target_type in (np.int64, np.int32):
    #     # Classification
    #     dummies = pd.get_dummies(df[target])
    #     print("dummies.values.shape",df[target].shape)
    #     # as_matrix is deprecated
    #     #return df.as_matrix(result).astype(np.float32), dummies.as_matrix().astype(np.float32)
    #     return df[result].values.astype(np.float32), dummies.values.astype(np.float32)
    # else:
    #     # Regression
    #     # as_matrix is deprecated
    #     #return df.as_matrix(result).astype(np.float32), df.as_matrix([target]).astype(np.float32)
    #     return df[result].values.astype(np.float32), df[target].values.astype(np.float32)

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


def process_dataset(df, sample, drop, lstm):
    if sample != None:
        if sample >= 1.0:
            print("invalid sample rate")
            exit(1)
    
        if sample <= 0:
            print("invalid sample rate")
            exit(1)
    
    print("[INFO] sampling", sample)
    df = df.sample(frac=sample, replace=False)

    if drop is not None:
        for col in drop.split(","): 
            drop_col(col, df)

    # Always drop columns that are unique for every record
    drop_col('UID', df)

    # Tag is always 0, remove this column
    drop_col('Tag', df)

    if not lstm:
        print("dropping all time related columns...")
        drop_col('Timestamp', df)
        drop_col('num', df)
        drop_col('date', df)
        drop_col('time', df)

    drop_col('SessionID', df)

    print("[INFO] columns:", df.columns)
   
def expand_categories(values):
    result = []
    s = values.value_counts()
    t = float(len(values))
    for v in s.index:
        result.append("{}:{}%".format(v,round(100*(s[v]/t),5)))
    return "[{}]".format(",".join(result))

def analyze(df):
    print()
    print("[INFO] analyzing data")
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

def encode_columns(df, result_column, lstm, debug):

    if debug:
        print("--------------BEFORE----------------")
        print("df.columns", df.columns, len(df.columns))
        with pd.option_context('display.max_rows', 10, 'display.max_columns', None):  # more options can be specified also
            print(df)

    for col in df.columns:
        colName = col.strip()
        if colName != result_column:
            if colName in encoders:
                encoders[colName](df, col)
            else:
                #print("[INFO] could not locate", colName, "in encoder dict. Defaulting to encode_numeric_zscore")
                encode_numeric_zscore(df, col)

    # Since this is now done in to_xy, we can skip encoding the result column here
    # Encode result as text index
    #print("[INFO] result_column:", result_column)
    #outcomes = encode_string(df, result_column)
    # Print number of classes
    #num_classes = len(outcomes)
    #print("[INFO] num_classes", num_classes)

    if debug:
        print("--------------AFTER ENCODING----------------")
        print("df.columns", df.columns, len(df.columns))
        with pd.option_context('display.max_rows', 10, 'display.max_columns', None):  # more options can be specified also
            print(df)
    
    # Remove entirely incomplete columns after encoding
    # TODO: apparently this also removes columns that contain only a single identical value for all rows
    # this behavior is undocumented, and breaks our code
    # because it changes the dimensionality of the input vector for some batches
    df.dropna(inplace=True, axis=1, how="all")

    if lstm:
        # drop last elem from dataframe, in case it contains an uneven number of elements
        if len(df) % 2 != 0:
            print("odd number of items, dropping last one...")
            df = df.iloc[:-1]

    if debug:
        print("--------------AFTER DROPPING INCOMPLETE COLUMNS ----------------")
        print("df.columns", df.columns, len(df.columns))
        with pd.option_context('display.max_rows', 10, 'display.max_columns', None):  # more options can be specified also
            print(df)

def create_dnn(input_dim, output_dim, loss, optimizer, lstm, numCoreLayers, coreLayerSize, dropoutLayer, lstmBatchSize, wrapLayerSize):

    # Create neural network
    # Type Sequential is a linear stack of layers
    model = Sequential()
    
    if lstm:

        # construct input shape
        input_shape=(int(lstmBatchSize/2),input_dim,)
        print("> input_shape", input_shape)

        print("> LSTM first and last layer neurons:", wrapLayerSize)

        # - The input of the LSTM is always a 3D array. (batch_size, time_steps, seq_len)
        # - The output of the LSTM could be a 2D array or 3D array depending upon the return_sequences argument.
        # - If return_sequence is False, the output is a 2D array. (batch_size, units)
        # - If return_sequence is True, the output is a 3D array. (batch_size, time_steps, units)

        model.add(layers.LSTM(wrapLayerSize, input_shape=input_shape, return_sequences=True))

        # add requested number of core layers
        for i in range(0, numCoreLayers):
            print("adding core layer", i)
            model.add(layers.LSTM(coreLayerSize, input_shape=input_shape, return_sequences=True))

        # add final LSTM layer
        model.add(layers.LSTM(wrapLayerSize, input_shape=input_shape, return_sequences=True))

        # add dropout layer if requested
        if dropoutLayer:
            model.add(Dropout(rate=0.5))

        # flatten if requested
        # TODO: currently this breaks the shape
        #model.add(Flatten())

        # final layer
        model.add(layers.Dense(output_dim, activation='softmax'))
    else:

        print(colored("[INFO] using Sequential Dense layers", 'yellow'))

        # DNN
        # add layers
        # first layer has to specify the input dimension
        model.add(Dense(wrapLayerSize, input_dim=input_dim, kernel_initializer='normal', activation='relu'))

        # add requested number of core layers
        for i in range(0, numCoreLayers):
            print("adding core layer", i)
            model.add(Dense(coreLayerSize, input_dim=input_dim, kernel_initializer='normal', activation='relu'))

        model.add(Dense(wrapLayerSize, input_dim=input_dim, kernel_initializer='normal', activation='relu'))
        model.add(Dense(1, kernel_initializer='normal'))
        model.add(Dense(output_dim, activation='softmax'))

    # metrics for model
    METRICS = [
        keras.metrics.TruePositives(name='tp'),
        keras.metrics.FalsePositives(name='fp'),
        keras.metrics.TrueNegatives(name='tn'),
        keras.metrics.FalseNegatives(name='fn'),
        keras.metrics.BinaryAccuracy(name='accuracy'),
        keras.metrics.Precision(name='precision'),
        keras.metrics.Recall(name='recall'),
        keras.metrics.AUC(name='auc'),
    ]

    # compile model
    #
    model.compile(
        loss=loss, 
        optimizer=optimizer, 
        metrics=METRICS
    )

    return model
