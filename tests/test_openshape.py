

import pytest
import pandas as pd
import pathlib
from DSreader import ReadPolyShape

@pytest.fixture
def root():
    return r'.\data\DSprojects\\'

@pytest.fixture
def goodshape(root):
    return root+'Drenthe\\Dr 0007_Hijken_1989\\vlakken.shp'

@pytest.fixture
def badshape(root):
    return root+'Limburg\\0892_Schuitwater_2013\\vlakken.shp'

def test_init_invalid_filepath(goodshape):
    shp = ReadPolyShape(goodshape,fix_errors=True)
    assert shp.error()['msg'] is None

def test_init_invalid_filepath(root):
    with pytest.raises(Exception) as e_info:
        badpath = root+'doesnotexist.shp'
        bad = OpenPolyShape(badpath)

def test_open_ringerror_shapefile(badshape):
    shp = ReadPolyShape(badshape,fix_errors=False)
    msg = "ValueError('A LinearRing must have at least 3 coordinate tuples')"
    assert msg in shp.error()['msg']

def test_fix_ringerror_shapefile(badshape):
    shp = ReadPolyShape(badshape,fix_errors=True)
    assert shp.error() is None

def test_open_missing_shx(goodshape):
    
    shx = goodshape.replace('shp','shx')
    filepath = pathlib.Path(shx)
    if filepath.is_file():
        filepath.unlink()# delete .shx
    msg = 'Set SHAPE_RESTORE_SHX config option to YES to restore or create it.'
    shp = ReadPolyShape(goodshape,fix_errors=False)
    assert msg in shp.error()['msg']

def test_fix_missing_shx(goodshape):
    shp = ReadPolyShape(goodshape,fix_errors=True)
    assert shp.error() is None

def test_columns(goodshape):
    shp = ReadPolyShape(goodshape,fix_errors=True)
    assert isinstance(shp.columns(),list)

def test_shape(goodshape):
    shp = ReadPolyShape(goodshape,fix_errors=True)
    assert isinstance(shp.shape(),pd.DataFrame)
