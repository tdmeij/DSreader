
import pytest
from pandas import Series, DataFrame
import pandas as pd
from geopandas import GeoSeries, GeoDataFrame
from DSreader import MapData


@pytest.fixture
def mpd():
    srcdir = r'.\data\DSprojects\Drenthe\Dr 0469_Hijken_2001\\'
    mdbpath = f'{srcdir}469_Hijken.mdb'
    polypath = f'{srcdir}vlakken.shp'
    linepath = f'{srcdir}lijnen.shp'
    mpd = MapData.from_filepaths(mdbpath=mdbpath,polypath=polypath,linepath=linepath,
        mapname='Hijken_2001',mapyear='2001')
    return mpd

def test_boundary(mpd):
    assert isinstance(mpd.boundary,GeoSeries)

def test_polygons(mpd):
    assert isinstance(mpd.polygons,GeoDataFrame)

def test_lines(mpd):
    assert isinstance(mpd.lines,GeoDataFrame)

def test_mapname(mpd):
    assert isinstance(mpd.mapname,str)

def test_mapyear(mpd):
    assert isinstance(mpd.mapyear,str)

def test_get_vegtype(mpd):
    assert isinstance(mpd.get_vegtype(),GeoDataFrame)

def test_get_vegtype_singlepoly(mpd):
    assert isinstance(mpd.get_vegtype_singlepoly(),GeoDataFrame)

def test_get_mapspecies(mpd):
    assert isinstance(mpd.get_mapspecies(),GeoDataFrame)

def test_get_pointspecies(mpd):
    assert isinstance(mpd.get_pointspecies(),GeoDataFrame)

def test_get_abiotiek(mpd):
    assert isinstance(mpd.get_abiotiek(),GeoDataFrame)


