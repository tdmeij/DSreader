
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

def test_init_has_projects_dataframe(lp):
    assert(isinstance(lp._projects,pd.DataFrame))

def test_repr(lp):
    assert isinstance(str(lp),str)

def get_root(lp):
    assert isinstance(lp.get_root(),str)

def test_listprojects(lp):
    result = lp.list_projects()
    assert(isinstance(result,pd.DataFrame))
    assert not result.empty

def test_mdb_listprojectfiles(lp):
    result = lp.list_projectfiles(filetype='.mdb',colname='mdb')
    assert(isinstance(result,pd.DataFrame))
    assert not result.empty

def test_shp_listprojectfiles(lp):
    result = lp.list_projectfiles(filetype='.shp',colname='shp')
    assert(isinstance(result,pd.DataFrame))
    assert not result.empty

def test_listprojectfiles_counts(lp):
    result = lp.list_projectfiles_counts(filetype='mdb',filetags=None,
        pathtags=None)
    assert isinstance(result,pd.DataFrame)
    assert not result.empty

    result = lp.list_projectfiles_counts(filetype='mdb',
        filetags=['foo','bar'],pathtags=['foo','bar'])
    assert isinstance(result,pd.DataFrame)
    assert not result.empty

def test_listprojectfiles_duplicates(lp):
    result = lp.list_projectfiles_duplicates(filetype='mdb',filetags=None,
        pathtags=None)
    assert isinstance(result,pd.DataFrame)

    result = lp.list_projectfiles_duplicates(filetype='mdb',
        filetags=['foo','bar'],pathtags=['foo','bar'])
    assert isinstance(result,pd.DataFrame)

"""
def test_selectfiletype_mdb(lp):
    result = lp._selectfiles('.mdb',guessfile=True)
    assert(isinstance(result,pd.DataFrame))
    assert not result.empty

def test_selectfiletype_shp(lp):
    result = lp._selectfiles('.shp',guessfile=True)
    assert(isinstance(result,pd.DataFrame))
    assert not result.empty

def test_projectfiletable(lp):
    result = lp.list_projectfiletable(relpaths=True)
    assert(isinstance(result,pd.DataFrame))
    assert not result.empty

def check_selection(filetype=None,filename='test.xlsx'):
    result = lp.check_selection(relpaths=True)
    assert(isinstance(result,pd.DataFrame))
    assert not result.empty
"""