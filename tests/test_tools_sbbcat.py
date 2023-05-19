
import pytest
from pandas import Series
from DSreader.tools.sbbcat import get_class
from DSreader.tools.sbbcat import get_synlevel
from DSreader.tools.sbbcat import syntaxon_levels
import DSreader

@pytest.fixture
def syn():
    return DSreader.data.get_sbbcat_syntaxa()

@pytest.fixture
def synlev_names():
    return list(DSreader.tools.sbbcat.REGDICT.keys())

def test_get_class(syn):
    syn['çatcode'] = syn.index
    sr = syn['çatcode'].apply(get_class)
    assert isinstance(sr,Series)
    assert not sr.empty

def test_get_synlevel(syn):
    syn['çatcode'] = syn.index
    sr = syn['çatcode'].apply(get_synlevel)
    assert isinstance(sr,Series)
    assert not sr.empty
    
def test_syntaxon_levels(syn):
    synlev = syntaxon_levels()
    assert isinstance(synlev,list)
 
def test_results(synlev_names):
    syntaxa = ['09','09-a','09/b','09A','09A-a','09A/a','09A1','09A2a',]
    results = []
    for item in syntaxa:
        res = get_synlevel(item)
        assert res is not None
        results.append(res)
    assert sorted(results) == sorted(synlev_names)
