

import pytest
from pandas import DataFrame
from geopandas import GeoDataFrame
from DSreader import Tv2
##from collections import OrderedDict
import pandas as pd


@pytest.fixture
def db():
    folder = r'.\data\DSprojects\Drenthe\Dr 0007_Hijken_1989\TV_7\\'
    db = Tv2(folder, prjname='Hijken 1989')
    assert isinstance(db, Tv2)
    return db

def test_invalid_folder():
    with pytest.raises(Exception) as e_info:
        Tv2('no valid folder path')

def test_len(db):
    assert len(db) != 0

def test_tvhabita(db):
    assert isinstance(db.tvhabita, DataFrame)

def test_tvabund(db):
    assert isinstance(db.tvabund, DataFrame)

def test_remarks(db):
    assert isinstance(db._remarks, DataFrame)

def test_years(db):
    assert isinstance(db.years, list)
    assert len(db.years)>0

def test_isempty(db):
    assert not db.is_empty

def test_has_sbb(db):
    assert db.has_sbbcols

def test_locations(db):
    assert isinstance(db.locations, GeoDataFrame)

def test_usercols(db):
    assert isinstance(db.usercols, list)
    assert len(db.usercols)>0