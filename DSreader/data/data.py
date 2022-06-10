"""
Datasets included with DSreader.

bht_ken
    Characteristic vegetation types for each management type
    
"""

import pkg_resources
import pandas as pd

def bht_ken():
    """Return dataframe with characteristic vegetion types for all
    management types.
    
    Column kenm contains four classes:
    1 : Very characteristic
    2 : Characteristic
    3 : Less characteristic
    4 : Not characteristic for this management type
    """

    # This is a stream-like object. If you want the actual info, call
    # stream.read()
    stream = pkg_resources.resource_stream(__name__, 'beheertypen_kenmerkendheid.csv')
    return pd.read_csv(stream, encoding='latin-1')

