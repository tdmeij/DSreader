
import pkg_resources as _pkg_resources
import pandas as _pd


def get_tvabund():
    """Table definition of Turboveg2 tvabdund.dbf file."""
    stream = _pkg_resources.resource_stream(__name__,'definition_tvabund.csv')
    data = _pd.read_csv(stream, encoding='latin-1')
    data.columns = data.columns.str.lower()
    data = data.set_index('fieldnumber')
    return data


def get_tvabund_types():
    data = get_tvabund()
    typedict = dict(zip(
        data['fieldname'].values,
        data['type'].values,
        ))
    return typedict

def get_tvhabita():
    """Table definition of Turboveg2 tvhabita.dbf file."""
    stream = _pkg_resources.resource_stream(__name__,'definition_tvhabita.csv')
    data = _pd.read_csv(stream, encoding='latin-1')
    data.columns = data.columns.str.lower()
    data = data.set_index('fieldnumber')
    return data


def get_remarks():
    """Table definition of Turboveg2 remarks.dbf file."""
    stream = _pkg_resources.resource_stream(__name__,'definition_remarks.csv')
    data = _pd.read_csv(stream, encoding='latin-1')
    data.columns = data.columns.str.lower()
    data = data.set_index('fieldnumber')
    return data
