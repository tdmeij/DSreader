
import pytest
import pandas as pd
from DSreader import ListProjects

@pytest.fixture
def lp():
    rootpath = r'.\data\DSprojects\\'
    lp = ListProjects(rootpath)
    return lp

def test_init_goodpath(lp):
    assert(isinstance(lp,ListProjects))

def test_init_badpath():
    with pytest.raises(Exception) as e_info:
        badpath = r'..\01_source\wrongdir\\'
        lp = ListProjects(badpath)

def test_init_nonetype():
    with pytest.raises(Exception) as e_info:
        lp = ListProjects(None)

def test_repr(lp):
    assert isinstance(str(lp),str)

def test_listprojects(lp):
    result = lp.list_projects()
    assert(isinstance(result,pd.DataFrame))
    assert not result.empty

def test_listfiles(lp):
    result = lp.list_files(filetype='.mdb')
    assert(isinstance(result,pd.DataFrame))
    assert not result.empty

    result = lp.list_files(filetype='.shp')
    assert(isinstance(result,pd.DataFrame))
    assert not result.empty

def test_projectfiles_counts(lp):
    table = lp.list_files(filetype='.mdb')
    result = lp.projectfiles_counts(table,colname='mdbfile',
        fill_missing=True)
    assert isinstance(result,pd.DataFrame)
    assert not result.empty

def test_selectfiletype_mdb(lp):
    mdblist = lp.list_files('mdb')
    result,mdbleft = lp.filter_mdbfiles(mdblist,default_tags=True)
    assert(isinstance(result,pd.DataFrame))
    assert not result.empty

def test_selectfiletype_shp(lp):
    shpfiles = lp.list_files(filetype='shp')
    result,shpleft = lp.filter_shapefiles(shpfiles,priority_filepaths=None)
    assert(isinstance(result,pd.DataFrame))
    assert not result.empty

def test_projectfiles_table(lp):
    result = lp.projectfiles_table(relpaths=True,discardtags=None,
        default_tags=True,mdbpaths=None,polypaths=None,linepaths=None,
        pointpaths=None)
    #TODO: test with mdbpaths and shppaths
    assert(isinstance(result,pd.DataFrame))
    assert not result.empty
