
import pytest
from pandas import Series, DataFrame
import DSreader

import DSreader.data.syntaxa as syntaxa
import DSreader.data.taxa as taxa
import DSreader.data.turboveg as tv

def test_rvvn():

    df = syntaxa.get_rvvn_syntables()
    assert isinstance(df, DataFrame)
    assert not df.empty

    df = syntaxa.get_rvvn_syntaxa()
    assert isinstance(df, DataFrame)
    assert not df.empty

    df = syntaxa.get_rvvn_statistics()
    assert isinstance(df, DataFrame)
    assert not df.empty

def test_sbbcat():

    df = syntaxa.get_sbbcat_syntaxa()
    assert isinstance(df, DataFrame)
    assert not df.empty

    df = syntaxa.get_sbbcat_characteristic()
    assert isinstance(df, DataFrame)
    assert not df.empty

def test_management_types():

    sr = syntaxa.get_management_types()
    assert isinstance(sr, Series)
    assert not sr.empty

def test_taxa():

    df = taxa.get_species_2017()
    assert isinstance(df, DataFrame)
    assert not df.empty

def test_turboveg():

    df = tv.get_tvabund()
    assert isinstance(df, DataFrame)
    assert not df.empty

    df = tv.get_tvhabita()
    assert isinstance(df, DataFrame)
    assert not df.empty

    df = tv.get_remarks()
    assert isinstance(df, DataFrame)
    assert not df.empty

    rec = tv.get_tvabund_types()
    assert isinstance(rec, dict)
    assert len(rec.keys())==4
    assert len(rec.values())==4

