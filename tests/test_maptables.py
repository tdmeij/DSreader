

import pytest
##from DSreader import Mdb
from pandas import Series, DataFrame
import pandas as pd
from DSreader import MapTables

@pytest.fixture
def db():
    srcdir = r'.\data\DSprojects\Drenthe\Dr 0469_Hijken_2001\\'
    mdbpath = f'{srcdir}469_Hijken.mdb'
    return MapTables.from_mdb(mdbpath)

@pytest.fixture
def empty_db():
    return MapTables()

def test_empty():
    assert isinstance(MapTables(),MapTables)
    assert len(MapTables())==0
    assert isinstance(str(MapTables()),str)

def test_basics(db):
    assert isinstance(db,MapTables)
    assert len(db)!=0
    assert isinstance(str(db),str)

def test_filepath(db):
    assert isinstance(db.filepath,str)

def test_from_mdb_badfilepath():
    with pytest.raises(Exception) as e_info:
        MapTables.from_mdb('badpath.mdb')

def test_get_abiotiek(db):
    assert isinstance(db.get_abiotiek(),DataFrame)

def test_get_mapspecies(db):
    assert isinstance(db.get_mapspecies(),DataFrame)

def test_get_pointspecies(db):
    assert isinstance(db.get_pointspecies(),DataFrame)

def test_get_vegtype(db):
    assert isinstance(db.get_vegtype(),DataFrame)

def test_yearcounts(db):
    assert isinstance(db.yearcounts,Series)

def test_get_mapyear(db):
    assert isinstance(db.get_mapyear(),int)

""" For developing
srcdir = r'.\data\DSprojects\Drenthe\Dr 0469_Hijken_2001\\'
mdbpath = f'{srcdir}469_Hijken.mdb'
mdb = dsr.Mdb(mdbpath)
db = dsr.MapTables.from_mdb(mdbpath)
"""