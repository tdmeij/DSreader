

import pytest
from pandas import Series, DataFrame
import pandas as pd
from DSreader import TvXml, Releve

xmlpath = r'.\data\tv\DRA1516.xml'

@pytest.fixture
def tvxml():
    return TvXml.from_file(xmlpath)

def test_from_file(tvxml):
    assert isinstance(tvxml,TvXml)

def test_len(tvxml):
    assert len(tvxml)>0

def test_repr(tvxml):
    assert isinstance(str(tvxml),str)

def guidnumbers(tvxml):
    assert isinstance(tvxml.guidnumbers, Series)
    assert not tvxml.guidnumbers.empty

def releve_numbers(tvxml):
    assert isinstance(releve_numbers, list)

def test_get_releve(tvxml):
    rel = tvxml.get_releve(tvxml.guids[0])
    assert isinstance(rel, Releve)
    # todo: add test for releve not empty!

def test_tvflora(tvxml):
    assert isinstance(tvxml.tvflora, DataFrame)

def test_tvhabita(tvxml):
    assert isinstance(tvxml.tvhabita, DataFrame)

def test_tvabund(tvxml):
    assert isinstance(tvxml.tvabund, DataFrame)

def test_xmlinfo(tvxml):
    assert isinstance(tvxml.xmlinfo, Series)

def test_get_coverscales(tvxml):
    assert isinstance(tvxml.get_coverscales(),DataFrame)

def test_lookuptables(tvxml):
    assert isinstance(tvxml.lookuptables, dict)

def test_lookuptablenames(tvxml):
    assert isinstance(tvxml.lookuptablenames,list)

def test_get_lookuptable(tvxml):
    # test with valid name
    assert isinstance(tvxml.get_lookuptable('Species_list'), DataFrame)
    # test with bas tablename
    with pytest.raises(Exception) as e_info:
        tvxml.get_lookuptable('bad_key')

def test_templates(tvxml):
    assert isinstance(tvxml.templates, dict)

def test_tvhabita_template(tvxml):
    assert isinstance(tvxml.tvhabita_template, DataFrame)
