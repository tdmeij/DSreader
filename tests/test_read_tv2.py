

import pytest
from pandas import DataFrame
from geopandas import GeoDataFrame
from DSreader import Tv2
##from collections import OrderedDict
import pandas as pd


@pytest.fixture
def db():
    folder = r'.\data\DSprojects\Drenthe\Dr 0007_Hijken_1989\TV_7\\'
    db = Tv2.from_folder(folder,prjname='Hijken 1989')
    assert isinstance(db,Tv2)
    return db

@pytest.fixture
def empty_db():
    db_empty = Tv2(prjname='empty project')
    assert isinstance(db_empty,Tv2)
    return db_empty

def test_invalid_folder():
    with pytest.raises(Exception) as e_info:
        Tv2.from_folder('no valid folder path')

def test_len(db, empty_db):
    assert len(db) != 0
    assert len(empty_db)==0

def test_tvhabita(db,empty_db):
    assert isinstance(db.tvhabita,DataFrame)
    assert empty_db.tvhabita.empty

def test_tvabund(db,empty_db):
    assert isinstance(db.tvabund,DataFrame)
    assert empty_db.tvabund.empty

def test_remarks(db,empty_db):
    assert isinstance(db._remarks,DataFrame)
    assert empty_db._remarks.empty

def test_years(db,empty_db):
    assert isinstance(db.years,list)
    assert len(db.years)>0
    assert len(empty_db)==0

def test_isempty(db,empty_db):
    assert not db.is_empty
    assert empty_db.is_empty

def test_contains_sbb(db,empty_db):
    assert db.contains_sbbcols
    assert not empty_db.contains_sbbcols

def test_get_locations(db,empty_db):
    assert isinstance(db.get_locations(),GeoDataFrame)
    assert empty_db.get_locations().empty
