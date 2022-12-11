
import pytest
import pandas as pd
from DSreader import ProjectsTable


@pytest.fixture
def ptable():
    rootpath = r'.\data\DSprojects\\'
    ptable = ProjectsTable(rootpath)
    return ptable


def test_init_goodpath(ptable):
    """Create ProjectsTable with valid project folder path."""
    assert(isinstance(ptable,ProjectsTable))


def test_init_badpath():
    """Try to create ProjectsTable with invalid project folder path."""
    with pytest.raises(Exception) as e_info:
        badpath = r'..\01_source\wrongdir\\'
        ptable = ListProjects(badpath)


def test_init_nonetype():
    """Try to create ProjectsTable with invalid None type input 
    for project folder path."""
    with pytest.raises(Exception) as e_info:
        ptable = ListProjects(None)


def test_repr(ptable):
    assert isinstance(repr(ptable),str)


def test_len(ptable):
    assert len(ptable)!=0


def test_listprojects(ptable):
    result = ptable.list_projects()
    assert(isinstance(result,pd.DataFrame))
    assert not result.empty


def list_files(ptable):
    result = ptable.list_files(filetype='.mdb')
    assert(isinstance(result,pd.DataFrame))
    assert not result.empty


    result = ptable.list_files(filetype='.shp')
    assert(isinstance(result,pd.DataFrame))
    assert not result.empty


def test_projectfiles_counts(ptable):
    table = ptable.list_files(filetype='.mdb')
    result = ptable.projectfiles_counts(table,colname='mdbfile',
        fill_missing=True)
    assert isinstance(result,pd.DataFrame)
    assert not result.empty

def test_filter_mdbfiles(ptable):
    """Test filter_mdbfiles with default parameter values."""
    mdblist = ptable.list_files('mdb')

    result, ambigous = ptable.filter_mdbfiles(mdblist,default_tags=True)
    assert(isinstance(result,pd.DataFrame))
    assert not result.empty
    assert(isinstance(ambigous,pd.DataFrame))
    assert not ambigous.empty

def test_filter_mdbfiles(ptable):
    """Test filter_mdbfiles with tweeked parameter values."""
    mdblist = ptable.list_files('mdb')
    result, ambigous = ptable.filter_mdbfiles(discardtags=['Copy'])
    assert(isinstance(result,pd.DataFrame))
    assert not result.empty
    assert(isinstance(ambigous,pd.DataFrame))
    assert ambigous.empty


def test_filter_shapefiles(ptable):
    """Test filter_shapefiles with default parameter values."""
    shpfiles = ptable.list_files(filetype='shp')
    result,ambigous = ptable.filter_shapefiles(filetbl=shpfiles,shptype='polygon',colprefix=None,
        priority_filepaths=None)
    assert(isinstance(result,pd.DataFrame))
    assert not result.empty
    assert(isinstance(ambigous,pd.DataFrame))
    assert not ambigous.empty


def test_filter_shapefiles(ptable):
    """Test filter_shapefiles with priority_filepath parameter."""
    shpfiles = ptable.list_files(filetype='shp')
    result,ambigous = ptable.filter_shapefiles(filetbl=shpfiles,shptype='polygon',colprefix=None,
        priority_filepaths=['..\\Drenthe\\Dr 0271_De_Witten_2000\\vlakken.shp'])
    assert(isinstance(result,pd.DataFrame))
    assert not result.empty
    assert(isinstance(ambigous,pd.DataFrame))
    assert ambigous.empty


def test_list_projectfiles(ptable):
    result = ptable.list_projectfiles(relpaths=True,discardtags=None,
        default_tags=True,mdbpaths=None,polypaths=None,linepaths=None,
        pointpaths=None)
    #TODO: test with mdbpaths and shppaths
    assert(isinstance(result,pd.DataFrame))
    assert not result.empty


def test_list_tv2(ptable):
    result = ptable.list_tv2()
    assert(isinstance(result,pd.DataFrame))
    assert not result.empty
    