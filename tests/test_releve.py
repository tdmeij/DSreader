
import pytest
from pandas import Series, DataFrame
import pandas as pd
from DSreader import Releve

def test_init():
    emptyrel = Releve()
    assert isinstance(emptyrel,Releve)
    assert isinstance(str(emptyrel),str)
    assert len(emptyrel)==0
    assert isinstance(emptyrel.tvabund,DataFrame)
    assert isinstance(emptyrel.tvflora,DataFrame)
    assert isinstance(emptyrel.tvhabita,Series)

