"""

    
"""

import pkg_resources
import pandas as pd
import numpy as np


class PackageData:
    """Contains datasets and lookup tables:
    
    management_types
        Management type codes and names.

    characteristic_vegetation_types
        Characteristic vegetion types for all management types.

    sbbcat_syntaxa
        List of vegetation types within Staatsbosbeheer Catalogus.  
    
    """

    @property
    def characteristic_vegetation_types(self):
        """Return table with characteristic vegetion types for all
        management types.

        Column kenm contains four classes:
        1 : Very characteristic
        2 : Characteristic
        3 : Less characteristic
        4 : Not characteristic for this management type
        """

        # This is a stream-like object. If you want the actual info, call
        # stream.read()
        stream = pkg_resources.resource_stream(__name__, 'beheertypen_kenmerkendheid.csv')
        return pd.read_csv(stream, encoding='latin-1')


    @property
    def management_types(self):
        """Return table with management type codes and names"""
        tbl = self.characteristic_vegetation_types
        tbl = tbl[['bht_code','bht_naam']].copy()
        tbl = tbl.drop_duplicates().set_index('bht_code').squeeze()
        tbl = tbl.sort_index(ascending=True)
        tbl.name = 'management_types'
        return tbl


    @property
    def sbbcat_syntaxa(self):
        """Return table with list of vegetation types in the Staatsbosbeheer
        Catalogus."""
        stream = pkg_resources.resource_stream(__name__, 'sbbcat_syntaxonnames.csv')
        sbbcat = pd.read_csv(stream, encoding='latin-1')
        sbbcat = sbbcat.set_index('sbbcat_code').sort_index()
        return sbbcat

    @property
    def species_2017(self):
        """Species list from Synbiosys."""
        stream = pkg_resources.resource_stream(__name__, 'synbiosys_soorten_2017.csv')
        spec = pd.read_csv(stream, encoding='latin-1')
        spec.columns = map(str.lower,spec.columns)
        spec = spec.set_index('species_nr').sort_index()

        # last column 'fam_nr' in file is float instead of string
        spec['fam_nr'] = spec['fam_nr'].apply(
            lambda x:str(x).split('.')[0] if pd.notna(x) else np.nan)

        return spec

    @property
    def def_tvabund(self):
        """Table definition of Turboveg2 tvabdund.dbf file."""
        stream = pkg_resources.resource_stream(__name__,'definition_tvabund.csv')
        return pd.read_csv(stream, encoding='latin-1').set_index('FIELDNUMBER')

    @property
    def tvabund_types(self):
        pdata = self.def_tvabund
        return dict(zip(pdata.def_tvhabita.FIELDNAME.values,
            pdata.def_tvhabita.TYPE.values))

    @property
    def def_tvhabita(self):
        """Table definition of Turboveg2 tvhabita.dbf file."""
        stream = pkg_resources.resource_stream(__name__,'definition_tvhabita.csv')
        return pd.read_csv(stream, encoding='latin-1').set_index('FIELDNUMBER')

    @property
    def def_remarks(self):
        """Table definition of Turboveg2 remarks.dbf file."""
        stream = pkg_resources.resource_stream(__name__,'definition_remarks.csv')
        return pd.read_csv(stream, encoding='latin-1').set_index('FIELDNUMBER')
