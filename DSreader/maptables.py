
import numpy as np
from pandas import Series, DataFrame
import pandas as pd
from collections import OrderedDict
import warnings
from .read.mdb import Mdb


class MapTables:
    """
    Contains tables from Digital Standard vegetation map.

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

    Class methods
    ------------
        from_mdb
            Create MapTables object from Microsoft Access mdb filepath.

    Notes
    -----
    A mapped element can be a polygon or a line. Spatial data for mapped
    elements are stored in shapefiles and linked to the MapTables data by 
    the attribute ElmID. Use MapData object to read both tables from 
    Microsoft mdb file and mappend elements from shapefiles.
    
    """

    MAPPING_COLNAMES = OrderedDict({
        'Element' : {
            'intern_id' : 'locatie_id',
            'samengesteldelegenda':'vegtype_combi_code', 
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
        'LegendaHulp' : {
            'samengesteld':'vegtype_combi_code', 
            'gegevens':'karteer_item', 
            'omschrijving':'vegtype_combi_naam',
            'aantal':'aantal_elementen',
            'vereenvoudigd':'vegtype_eenvoudig_code',
            'landtypened':'sbbcat_combi_nednaam',
            'landtypewet':'sbbcat_combi_wetnaam', 
            'opp':'opp_ha', 
            'sbbtype':'sbbcat_combi_code',
            },
        'VereenvoudigdeLegenda' : {
            'code':'vegtype_eenvoudig_code',
            'omschrijving':'vegtype_eenvoudig_naam',
            },
        })


    def __init__(self,tables=None,filepath=None): ##,mdb=None):
        """
        Parameters
        ----------
        tables : OrderedDict
            Dictionary of tables from mdb file.
        mdb : ReadMdb object, optional
            Original source with tables.

        Notes
        -----
        Use classmethod MapTables.from_mdb(<filepath>) to create a 
        MapTables instance with data from a Microsoft Access mdb file.
        """
        self._tbldict = tables
        self._filepath = filepath

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
            return cls(tables=None)

        # all mdb tables to dict
        mdbtables = mdb.all_tables
        maptables = {}
        for tblname in mdbtables.keys():
            mdbtbl = mdbtables[tblname]
            mdbtbl.columns = map(str.lower,mdbtbl.columns)
            if tblname in cls.MAPPING_COLNAMES.keys():
                mdbtbl = mdbtbl.rename(columns=cls.MAPPING_COLNAMES[tblname])
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

        return cls(tables=maptables,filepath=filepath)


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
        element = pd.merge(element,vegloc,how='left',left_on='locatie_id',
            right_on='locatie_id',suffixes=(None,'_vegloc'),
            validate='one_to_many')

        vegtype = self._tbldict['VegetatieType']
        element = pd.merge(element,vegtype,how='left',left_on='vegtype_code',
            right_on='vegtype_code',suffixes=(None,'_vegtype'),
            validate='many_to_one')

        sbbtype = self._tbldict['SbbType']
        element = pd.merge(element,sbbtype,how='left',left_on='sbbcat_id',
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

    def get_vegtype_singlepoly(self,loctype='v'):
        """
        Return vegetation type for each mapped element. Each element is 
        returned only once. When multiple vegetation types are present
        in a mapped element, vegetation types are combined in a single
        code.

        Parameters
        ----------
        loctype : {'v','l'}, default 'l'
            Element location type

        Notes
        -----
        A mapped element can have multiple vegetation types (vegetation
        complexes). To avoid returning the same polygon multiple times,
        multiple vegetation types are combined in one code composed of
        the seperate vegetation types. These combined vegetation codes
        are stored in the Digital Standard database, this function 
        retrieves this already stored information and does not calculate
        them on the fly.
        """
    
        if loctype not in ['v','l']:
            warnings.warn((f'Loctype must be "v" of "l", not {loctype}. '
                f'Elements of loctyp "v" will be returned.'))
            loctype = 'v'

        # table ElmID
        elmcols = ['elmid', 'locatietype', 'datum','vegtype_combi_code',]

        mask = self._tbldict['Element']['locatietype']==loctype
        elmtbl = self._tbldict['Element'][mask][elmcols].copy()

        # table with legend 
        legcols = [
            'vegtype_combi_code', 'vegtype_combi_naam',
            'vegtype_eenvoudig_code','sbbcat_combi_code','sbbcat_combi_nednaam',
            'sbbcat_combi_wetnaam',]
        mask = self._tbldict['LegendaHulp']['karteer_item']=='vegetatie'
        legtbl = self._tbldict['LegendaHulp'][mask][legcols].copy()

        # add description to legend table
        legtbl = pd.merge(legtbl,self._tbldict['VereenvoudigdeLegenda'],
            left_on='vegtype_eenvoudig_code',right_on='vegtype_eenvoudig_code',
            how='left')

        # merge Elments with combined legend
        singlepoly = pd.merge(elmtbl,legtbl,left_on='vegtype_combi_code',
            right_on='vegtype_combi_code',how='left')

        return singlepoly


    def get_pointspecies(self):
        """Return table of point locations for mapped plant species"""

        # if no pointspecies table is present
        colnames = list(self.MAPPING_COLNAMES['PuntLocatieSoort'].values())
        emptytbl = DataFrame(columns=colnames)
        if self._tbldict is None:
            return emptytbl
        if 'PuntLocatieSoort' not in self._tbldict.keys():
            return emptytbl

        # create pointspecies export
        pntsrt = self._tbldict['PuntLocatieSoort'].copy()
        pntsrt['srtdatum'] = pntsrt['srtdatum'].apply(
            lambda x: x.strftime('%d%m%Y') if not pd.isna(x) else '')
        return pntsrt


    def get_mapyear(self,preference='count'):
        """Return single year of mapping.
        
        Parameters
        ----------
        preference : {'count','first','last'}, default 'count'
            Criterium to choose one mapping year from several possible
            years ('count':choose year with maximum number of mapped 
            elements, 'first': choose first year, 'last': choose last year.

        Return
        ------
        int | None
        """
        year = None

        if self.yearcounts.empty: #no valid years found
            return None

        if len(self.yearcounts)==1: #exactly one valid year found
            return int(self.yearcounts.index[0])

        if preference=='count':
            year = self.yearcounts.idxmax()

        # if multiple mapping years are present, return last or first 
        # year, but only if no years in between are missing.
        if preference in ['first','last']:
            years = self.yearcounts.index.to_list()
            years_subsequent = [(years[i]-years[i-1])==1 for i in range(1,len(years))]
            if np.all(years_subsequent)==1:
                if preference=='last':
                    year = years[-1]
                else:
                    year = years[0]

        if year is not None:
            year = int(year)

        return year

    @property
    def empty(self):
        if self._maptbl._tbldict is None:
            return True
        return False

    @property
    def yearcounts(self):
        """Return number of mapped elements by year."""
        dates = pd.to_datetime(self._tbldict['Element']['datum'],errors='coerce')
        years = dates.dt.year.value_counts()
        years.name = 'elements'
        years.index.name = 'jaar'

        if years.empty:
            warnings.warn((f'No valid dates in {self._filepath}.'),stacklevel=1)

        return years.sort_index()
    

    def get_mapspecies(self,loctype='all'):
        """Return species data attached to mapped elements.

        Parameters
        ----------
        loctype : {'all','v','l'}, default 'all'
            Results contain only values for this location type.

        Returns
        -------
        pandas.DataFrame

        Note
        ----
        Multiple species can be mapped for a map element. Values for
        field ElmID will not be unique for this reason.
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
        """Return table with abiotic observatons.
        
        Parameters
        ----------
        loctype : '{'all','v','l'}, default 'all'

        Returns
        -------
        pandas.Dataframe
        """

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


    @property
    def filepath(self):
        """Return filepath to source of tables."""
        return self._filepath









