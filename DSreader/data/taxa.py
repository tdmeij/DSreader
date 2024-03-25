

import pkg_resources as _pkg_resources
import pandas as _pd
import numpy as _np


def get_species_2017():
    """Species list from Synbiosys."""
    stream = _pkg_resources.resource_stream(__name__, 'synbiosys_soorten_2017.csv')
    spec = _pd.read_csv(stream, encoding='latin-1')
    spec.columns = map(str.lower,spec.columns)
    spec = spec.set_index('species_nr').sort_index()

    # last column 'fam_nr' in file is float instead of string
    spec['fam_nr'] = spec['fam_nr'].apply(
        lambda x:str(x).split('.')[0] if _pd.notna(x) else _np.nan)

    return spec
