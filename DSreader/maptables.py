

from pandas import Series, DataFrame
import pandas as pd
from collections import OrderedDict
import warnings
from .read.mdb import Mdb


class MapTables:
    """
    Tables with data related to vegetation map elements

    Methods
    -------
        get_vegtype
            Return vegetation type for each mapped element.
        get_mapspecies
            Return species data attached to mapped elements.
        get_abiotiek
            Return environmental field observatons attached to mapped 
            elements.
        get_pointspecies
            Return point locations for mapped plant species.
        get_year
            Return year of mapping, returns 0000 if no dates are present.

    Classmethods
    ------------
        from_mdb
            Create MapTables object from Microsoft Access mdb filepath.

    Notes
    -----
    A mapped element can be a polygon or a line. Spatial data for these
    elements are stored in shapefiles and linked to the table data by 
    the attribute ElmID.
    
    """

    _DS_tablenames = ['vegetatietype','sbbtype']

    _mapping_colnames = OrderedDict({
        'Element' : {
            'intern_id' : 'locatie_id',
            },
        'KarteringVegetatietype' : {
            'locatie': 'locatie_id',
            'vegetatietype': 'vegtype_code',
            'bedekking':'vegtype_bedekkingcode',
            'bedekking_num':'vegtype_bedekkingnum',
            },
        'VegetatieType' : {
            'typenummer':'vegtype_nr',
            'code':'vegtype_code',
            'gemeenschap':'vegtype_naam',
            'vorm':'vegtype_vorm',
            'sbbtype':'sbbcat_id',
            'sbbtype2':'sbbcat2_id',
            'opmerking':'vegtype_note',
            },
        'SbbType': {
            'cata_id':'sbbcat_id',
            'versie':'sbbcat_versie',
            'code':'sbbcat_code',
            'klassenaamned':'sbbcat_klassenaam',
            'verbrgnaamned':'sbbcat_kortenaam',
            'asscocrgnaamned':'sbbcat_assrgnaam',
            'subassocnaamned':'sbbcat_subassnaam',
            'landtypened':'sbbcat_nednaam',
            'landtypewet':'sbbcat_wetnaam',
            'vervallen':'sbbcat_vervallen',
            'vervangbaarheid':'sbbcat_vervangbaarheid',
            },
        'KarteringSoort': {
            'locatie':'locatie_id', 
            'soortcode':'krtsrt_srtcode', 
            'bedekking':'krtsrt_bedcode', 
            'aantalsklasse':'krtsrt_aantalsklasse', 
            'bedekking_num':'krtsrt_bednum',
            },
        'CbsSoort':{
            'soortnr':'cbs_srtcode',
            'floron':'cbs_floron',
            'wetenschap':'cbs_srtwet',
            'nederlands':'cbs_srtned',
            'zeldzaamheidsklasse':'cbs_zeldzaamheid',
            'trendklasse':'cbs_trend',
            'rl2000':'cbs_rl2000',
            'rl2000kort':'cbs_rl2000kort',
            },
        'PuntLocatieSoort': {
            'id':'pntid',
            'loctype':'pntloctype',
            'x_coord':'xcr',
            'y_coord':'ycr',
            'groep':'srtgroep',
            'nummer':'srtnr',
            'naam':'srtnednaam',
            'wetens':'srtwetnaam',
            'sbb_kl':'srtsbbkl',
            'tansley':'srttansley',
            'datum':'srtdatum',
            'waarn':'srtwrnmr',
            'opm':'srtopm',
            },
        'KarteringAbiotiek': {
            'locatie':'locatie_id',
            'abiotiek':'abio_code',
            },
        'Abiotiek': {
            'code':'abio_code',
            'omschrijving':'abio_wrn',
            },
        })


    def __init__(self,tables=None,filepath=None): ##,mdb=None):
        """
        Parameters
        ----------
        tables : OrderedDict
            Dictionary of tables from mdb file
        mdb : ReadMdb object, optional
            Original source with tables

        Notes
        -----
        Use classmethod MapTables.from_mdb(<filepath>) to create a 
        MapTables instance with data from a Microsoft Access mdb file.
        """

        self._tbldict = tables
        ##self._mdb = mdb
        self._filepath = filepath
        #if mdb is not None:
        #    self._filepath = mdb.filepath()

    def __repr__(self):
        return f'MapTables (n={self.__len__()})'

    def __len__(self):
        nelm = 0
        if self._tbldict:
            nelm = len(self._tbldict['Element'])
        return nelm

    @classmethod
    def from_mdb(cls,filepath):
        """
        Create MapTables object from Microsoft Access mdb filepath."

        Parameters
        ----------
        filepath : str
            valid filepath to Microsoft Access mdb file

        Returns
        -------
        MapTables 
        """

        if not isinstance(filepath,str):
            fptype = type(filepath)
            raise ValueError (f'Parameter filepath must be type "str" '
                f'not type {fptype}.')

        # open mdb file and check format is Digitale Standaard
        mdb = Mdb(filepath)

        # After mdb readerror return empty MapTables object
        if not mdb.all_tables:
            return cls(tables=None) ##,mdb=mdb)

        #if any([item in mdb.tablenames() for item in cls._DS_tablenames]):
        #    raise Exception(f'{mdb} is not a valid Digitale Standaard database.')

        # all mdb tables to dict
        mdbtables = mdb.all_tables
        maptables = {}
        for tblname in mdbtables.keys():
            mdbtbl = mdbtables[tblname]
            mdbtbl.columns = map(str.lower,mdbtbl.columns)
            if tblname in cls._mapping_colnames.keys():
                mdbtbl = mdbtbl.rename(columns=cls._mapping_colnames[tblname])
            maptables[tblname] = mdbtbl

        # clean tables: numeric to string type
        maptables['Element'] = maptables['Element'].astype(
            {'locatie_id':str,'elmid':str,})
        maptables['KarteringVegetatietype']=maptables['KarteringVegetatietype'].astype(
            {'locatie_id':str,})
        maptables['VegetatieType'] = maptables['VegetatieType'].astype(
            {'sbbcat_id': str, 'sbbcat2_id': str,}) 
        maptables['SbbType'] = maptables['SbbType'].astype(
            {"sbbcat_id": str, "sbbcat_versie": str, "sbbcat_vervangbaarheid": str,}) 
        maptables['KarteringSoort']=maptables['KarteringSoort'].astype(
            {'locatie_id':str,'krtsrt_srtcode':str,})
        maptables['CbsSoort']=maptables['CbsSoort'].astype(
            {'cbs_srtcode':str,})
        maptables['KarteringAbiotiek']=maptables['KarteringAbiotiek'].astype(
            {'locatie_id':str,})

        # clean tables : change vevangbaarheid 5.0 to 5 stingtype
        maptables['SbbType']['sbbcat_vervangbaarheid']=maptables['SbbType']['sbbcat_vervangbaarheid'].str[:1]

        # clean tables : convert column locatietype to lowercase
        # (locatietype can be: 'v','l','V','L')
        maptables['Element']['locatietype'] = maptables['Element']['locatietype'].str.lower()

        # fix small errors that occur in just a few (or just one) mdbfiles
        # smallfix01
        colnames = maptables['Element'].columns
        if ((not 'sbbtype' in colnames) and ('sbbtype1' in colnames)):
            maptables['Element']=maptables['Element'].rename(
                columns={'sbbtype1':'sbbtype'})
            warnings.warn((f'Microsoft Access mdb file {filepath} '
                f'has invalid column name "sbbtype1". Renamed to abbtype.'))

        return cls(tables=maptables,filepath=filepath) ##,mdb=mdb)


    def get_vegtype(self,loctype='v',select='all'):
        """
        Return vegetation type for each mapped element.

        Parameters
        ----------
        loctype : {'v','l'}, default 'l'
            Element location type
        select : {'all','maxcov'}, default 'all'
            Select from multiple instances of polygon.
            maxcov : select vegetation type with largest numeric cover.
        Notes
        -----
        A mapped element can have multiple vegetation types. Therefore 
        the table returned can have multiple rows with the same value 
        for the map polygon id elmid. 

        The fields bedekking and bedekking_num show the cover a 
        vegetation type has within a map polygon.
        """
        if loctype not in ['v','l']:
            warnings.warn((f'Loctype must be "v" of "l", not {loctype}. '
                f'Elements of loctyp "v" will be returned.'))
            loctype = 'v'

        elmcolnames = ['locatie_id', 'elmid', 'locatietype', 'datum']
        element = self._tbldict['Element'][elmcolnames]
        isloctype = element['locatietype']==loctype
        element = element[isloctype].copy()

        vegloc = self._tbldict['KarteringVegetatietype']
        element = pd.merge(element,vegloc,left_on='locatie_id',
            right_on='locatie_id',suffixes=(None,'_vegloc'),
            validate='one_to_many')

        vegtype = self._tbldict['VegetatieType']
        element = pd.merge(element,vegtype,left_on='vegtype_code',
            right_on='vegtype_code',suffixes=(None,'_vegtype'),
            validate='many_to_one')

        sbbtype = self._tbldict['SbbType']
        element = pd.merge(element,sbbtype,left_on='sbbcat_id',
            right_on='sbbcat_id',suffixes=(None,'sbbtype'),
            validate='many_to_one')

        element['datum'] = element['datum'].apply(lambda x: x.strftime(
            '%d%m%Y') if not pd.isna(x) else '')

        colnames = ['elmid','datum','locatietype','vegtype_code',
            'vegtype_naam','vegtype_vorm','vegtype_bedekkingcode',
            'vegtype_bedekkingnum',
            'sbbcat_code', 'sbbcat_wetnaam','sbbcat_nednaam',
            'sbbcat_kortenaam','sbbcat_vervangbaarheid']
        element = element[colnames].copy()

        if select=='maxcov':
            element = element.sort_values(['elmid',
                'vegtype_bedekkingnum'],ascending=False)
            element = element.groupby('elmid').head(1)

        return element.copy()

    def get_pointspecies(self):
        """Return table of point locations for mapped plant species"""
        pntsrt = self._tbldict['PuntLocatieSoort'].copy()
        pntsrt['srtdatum'] = pntsrt['srtdatum'].apply(
            lambda x: x.strftime('%d%m%Y') if not pd.isna(x) else '')
        return pntsrt

    """
    def get_year(self):
        Return year of mapping, returns 0000 if no dates are present
        dates = pd.to_datetime(self._tbldict['Element']['datum'],errors='coerce')
        years = list(dates.dt.year.unique())

        if len(years)==1:
            if pd.isnull(years[0]):
                return '0000'
            return str(years[0])
        return str(min(years))+'-'+str(max(years))
    """

    def get_years(self):
        """Return frequency of mapped elements by year."""
        dates = pd.to_datetime(self._tbldict['Element']['datum'],errors='coerce')
        years = dates.dt.year.value_counts(sort=False)

        if years.empty:
            warnings.warn((f'No valid dates in {self._filepath}.'),stacklevel=1)
            ##return None

        return years

    def get_mapspecies(self,loctype='all'):
        """Return species data attached to mapped elements.

        Parameters
        ----------
        loctype : {'all','v','l'}, default 'all'
            Results contain only values for this location type.

        Returns
        -------
        pandas DataFrame

        Note
        ----
        Multiple species can be mapped for a map element. Values for
        field ElmID will therefore not be unique.
        """

        if loctype not in ['all','v','l']:
            raise ValueError(f'Invalid loctype {loctype}')

        elmcolnames = ['locatie_id', 'elmid', 'locatietype', 'datum','sbbtype']
        element = self._tbldict['Element'][elmcolnames]

        krtsrt = self._tbldict['KarteringSoort']
        mapspec = pd.merge(element,krtsrt,left_on='locatie_id',
            right_on='locatie_id',how='right',suffixes=(None,'_krtsrt'),
            validate='one_to_many')

        cbscolnames = ['cbs_srtcode','cbs_srtwet','cbs_srtned',]
        cbs = self._tbldict['CbsSoort'][cbscolnames]
        mapspec = pd.merge(mapspec,cbs,left_on='krtsrt_srtcode',
            right_on='cbs_srtcode',how='left',suffixes=(None,'_cbs'),
            validate='many_to_one')

        mapspec = mapspec.drop(columns=['locatie_id','cbs_srtcode'])

        if loctype in ['v','l']:
            mapspec = mapspec[mapspec['locatietype']==loctype]

        return mapspec


    def get_abiotiek(self,loctype='all'):
        """Return table of environmental observatons"""

        if loctype not in ['all','v','l']:
            raise ValueError(f'Invalid loctype {loctype}')

        elmcolnames = ['locatie_id', 'elmid', 'locatietype', 'datum']
        element = self._tbldict['Element'][elmcolnames]
        abi = self._tbldict['KarteringAbiotiek']
        mapabi = pd.merge(element,abi,left_on='locatie_id',
            right_on='locatie_id',how='left',suffixes=(None,'_abi'),
            validate='one_to_many')

        abicode = self._tbldict['Abiotiek']
        mapabi = pd.merge(mapabi,abicode,left_on='abio_code',
            right_on='abio_code',how='left',suffixes=(None,'_abicode'),
            validate='many_to_one')

        if loctype in ['v','l']:
            mapabi = mapabi[mapabi['locatietype']==loctype]

        mapabi = mapabi.drop(columns=['locatie_id'])
        return mapabi[mapabi['abio_code'].notnull()]

    def filepath(self):
        """Return filepath to source of tables."""
        return self._filepath









