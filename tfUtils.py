from termcolor import colored



def encode_string(df, name):
    """
    Encodes text values to indexes(i.e. [1],[2],[3] for red,green,blue).
    """
    # replace missing values (NaN) with an empty string
    df[name].fillna('',inplace=True)
    print(colored("encode_text_index " + name, "yellow"))
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

encoders = {
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


def process_dataset(df, sample, drop):
    if sample != None:
        if sample >= 1.0:
            parser.error("invalid sample rate")
    
        if sample <= 0:
            parser.error("invalid sample rate")
    
    print("[INFO] sampling", sample)
    df = df.sample(frac=sample, replace=False)

    if drop != None:
        for col in drop.split(","): 
            drop_col(col, df)

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

def encode_columns(df, result_column):
    for col in df.columns:
        colName = col.strip()
        if colName != result_column:
            if colName in encoders:
                encoders[colName](df, col)
            else:
                #print("[INFO] could not locate", colName, "in encoder dict. Defaulting to encode_numeric_zscore")
                encode_numeric_zscore(df, col)
    
    # Encode result as text index
    print("[INFO] result_column:", result_column)
    outcomes = encode_text_index(df, result_column)
    
    # Print number of classes
    num_classes = len(outcomes)
    print("[INFO] num_classes", num_classes)
    
    # Remove incomplete records after encoding
    df.dropna(inplace=True,axis=1) 
