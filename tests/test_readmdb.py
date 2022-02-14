
import pytest
from DSreader import ReadMdb
from collections import OrderedDict
import pandas as pd

@pytest.fixture
def root():
    return r'.\data\DSprojects\\'

@pytest.fixture
def goodpath(root):
    return root+'Drenthe\\Dr 0007_Hijken_1989\\7_Hijken.mdb'

@pytest.fixture
def mdb(goodpath):
    return ReadMdb(goodpath)

def test_tablesnames(mdb):
    res = mdb.tablenames()
    assert isinstance(res,list)
    assert len(res)!=0

def test_table(mdb):
    tablename = mdb.tablenames()[0]
    res = mdb.table(tablename)
    assert isinstance(res,pd.DataFrame)
    assert not res.empty

def test_all_tables(mdb):
    res = mdb.all_tables()
    assert isinstance(res,OrderedDict)
    assert list(res.keys())==mdb.tablenames()

