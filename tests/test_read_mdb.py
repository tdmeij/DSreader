
import pytest
from DSreader import Mdb
from collections import OrderedDict
from pandas import DataFrame
import pandas as pd

@pytest.fixture
def root():
    return r'.\data\DSprojects\\'

@pytest.fixture
def goodpath(root):
    return root+'Drenthe\\Dr 0007_Hijken_1989\\7_Hijken.mdb'

@pytest.fixture
def mdb(goodpath):
    return Mdb(goodpath)

@pytest.fixture
def badpath():
    return r'.\data\badfiles\532_Nieuwezuiderlingedijk.mdb'

@pytest.fixture
def badmdb(badpath):
    return Mdb(badpath)

   
def test_mdb_len(mdb,badmdb):
    assert len(mdb)!=0
    assert len(badmdb)==0

def test_mdb_repr(mdb, badmdb):
    assert isinstance(str(mdb),str)
    assert isinstance(str(mdb),str)

def test_tablesnames(mdb):
    res = mdb.tablenames
    assert isinstance(res,list)
    assert len(res)!=0

def test_get_table(mdb):
    res = mdb.get_table('Element')
    assert isinstance(res,pd.DataFrame)
    assert not res.empty

    # iterate over all tablenames
    for name in mdb.tablenames:
        tbl = mdb.get_table(name)
        assert isinstance(tbl,DataFrame)

def test_all_tables(mdb):
    res = mdb.all_tables
    assert isinstance(res,OrderedDict)
    assert list(res.keys())==mdb.tablenames

def test_read_error(goodpath, badpath):
    goodmdb = Mdb(goodpath)
    assert goodmdb.read_error is None
    badmdb = Mdb(badpath)
    assert isinstance(badmdb.read_error,dict)


""" For developing:
from DSreader import Mdb
root = r'.\data\DSprojects\\'
mdbpath = f'{root}Drenthe\\Dr 0007_Hijken_1989\\7_Hijken.mdb'
mdb = Mdb(mdbpath)
""" 