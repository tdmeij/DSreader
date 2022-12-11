"""
Datasets included with DSreader.

bht()
    Management type codes and names

bht_ken()
    Characteristic vegetation types for each management type
    
"""

import pkg_resources
import pandas as pd

def characteristic_vegetation_types():
    """Return table with characteristic vegetion types for all
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

def management_types():
    """Return table with management type codes and names"""
    tbl = characteristic_vegetation_types()
    tbl = tbl[['bht_code','bht_naam']].copy()
    tbl = tbl.drop_duplicates().set_index('bht_code').squeeze()
    tbl = tbl.sort_index(ascending=True)
    tbl.name = 'management_types'
    return tbl

def sbbcat_syntaxa():
    """Return table with list of vegetation types in the Staatsbosbeheer
    Catalogus."""
    stream = pkg_resources.resource_stream(__name__, 'sbbcat_syntaxonnames.csv')
    sbbcat = pd.read_csv(stream, encoding='latin-1')
    sbbcat = sbbcat.set_index('sbbcat_code').sort_index()
    return sbbcat
