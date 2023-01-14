
import pytest
import pandas as pd
from DSreader import year_from_string

def test_year_from_string():
    rawstring = 'Dr 0982 Wijster Terhorst 2017'
    result = year_from_string(rawstring, minyear=1960, maxyear=2050)
    assert isinstance(result,str)
    assert len(result)!=0

    result = year_from_string(rawstring, minyear=1960, maxyear=1970)
    assert isinstance(result,str)
    assert len(result)==0
