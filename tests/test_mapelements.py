

import pytest
from pandas import Series, DataFrame
import pandas as pd
from geopandas import GeoSeries, GeoDataFrame
from DSreader import MapElements


@pytest.fixture
def poly():
    srcdir = r'.\data\DSprojects\Drenthe\Dr 0469_Hijken_2001\\'
    polypath = f'{srcdir}vlakken.shp'
    poly = MapElements.from_shapefile(polypath)
    assert isinstance(poly,MapElements)
    return poly

@pytest.fixture
def line():
    srcdir = r'.\data\DSprojects\Drenthe\Dr 0469_Hijken_2001\\'
    linepath = f'{srcdir}lijnen.shp'
    line = MapElements.from_shapefile(linepath)
    assert isinstance(line,MapElements)
    return line


def test_basics(poly):
    assert isinstance(str(poly),str)
    assert len(poly)!=0

def test_boundary(poly,line):
    assert isinstance(poly.boundary,GeoSeries)
    assert isinstance(line.boundary,GeoSeries)

def test_colnames(poly,line):
    assert isinstance(poly.colnames,list)
    assert isinstance(line.colnames,list)

def test_filepath(poly,line):
    assert isinstance(poly.filepath,str)
    assert isinstance(line.filepath,str)

def test_shape_type(poly,line):
    assert poly.shape_type=='polygon'
    assert line.shape_type=='linestring'

def test_shape(poly,line):
    assert isinstance(poly.shape,GeoDataFrame)
    assert isinstance(line.shape,GeoDataFrame)

""" For developing
srcdir = r'.\data\DSprojects\Drenthe\Dr 0469_Hijken_2001\\'
mdbpath = f'{srcdir}469_Hijken.mdb'
mdb = dsr.Mdb(mdbpath)
db = dsr.MapTables.from_mdb(mdbpath)
poly = MapElements()
"""