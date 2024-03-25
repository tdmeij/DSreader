
import pytest
import pandas as pd
import pathlib
from DSreader import ShapeFile

@pytest.fixture
def root():
    return r'.\data\DSprojects\\'

@pytest.fixture
def goodshapepath(root):
    return root+'Drenthe\\Dr 0007_Hijken_1989\\vlakken.shp'

@pytest.fixture
def badshapepath(root):
    """Return path to shapefile with errors.
    
    Notes
    -----
    fid 234 has 1 ring with less than three nodes
    fid 368 has geometry type None
    """
    return root+'Limburg\\0892_Schuitwater_2013\\vlakken.shp'

@pytest.fixture
def emptyshapepath(root):
    """Return path to empty shapefile."""
    return root+'Noord-Brabant\\0851_Keersop en Run_2011\\lijnen.shp'

def test_open_goodfile(goodshapepath):
    """Test reading a valid shapefile"""
    readr = ShapeFile(goodshapepath)
    return

def test_shape(goodshapepath):
    """Test ReadShapeFile.shape()"""
    readr = ShapeFile(goodshapepath)
    assert isinstance(readr.shape, pd.DataFrame)

def test_shape_errors(goodshapepath):
    """Test ReadShapeFile.shape_errors()"""
    readr = ShapeFile(goodshapepath)
    assert isinstance(readr.shape_errors, pd.DataFrame)

def test_columns(goodshapepath):
    """Test ReadShapeFile.columns()"""
    readr = ShapeFile(goodshapepath)
    assert readr.columns # not empty list evaluates to True

def test_filepath(goodshapepath):
    """Test ReadShapeFile.filepath()"""
    readr = ShapeFile(goodshapepath)
    filepath = pathlib.Path(readr.filepath)
    assert filepath.is_file()

def test_init_invalid_filepath(root):
    """Test init with invalid filepath"""
    with pytest.raises(Exception) as e_info:
        badpath = root+'doesnotexist.shp'
        bad = ReadShapeFile(badpath)

def test_open_missing_shx(goodshapepath):
    """Test if file without .shx can be opened"""
    shx = goodshapepath.replace('shp','shx')
    filepath = pathlib.Path(shx)
    if filepath.is_file():
        filepath.unlink()# delete .shx
    ##msg = 'Set SHAPE_RESTORE_SHX config option to YES to restore or create it.'
    readr = ShapeFile(goodshapepath)
    assert not readr.shape.empty

def test_found_errors(badshapepath):
    """Test if known errors in shapefile are found"""
    readr = ShapeFile(badshapepath)
    err = readr.shape_errors

    msg = 'rings with less than three nodes'
    err['match'] = err['error'].apply(lambda x:msg in x)
    assert err['match'].any(axis=0)

    msg = r'Geometry type is None'
    err['match'] = err['error'].apply(lambda x:msg in x)
    assert err['match'].any(axis=0)

def test_empty_shape(emptyshapepath):
    """Test opening empty sdhapefile"""
    readr = ShapeFile(emptyshapepath)
    assert readr.shape.empty

