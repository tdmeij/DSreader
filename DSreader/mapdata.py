
from collections import OrderedDict
import warnings
from pandas import Series, DataFrame
import pandas as pd
import geopandas as gpd

from .maptables import MapTables
from .mapelements import MapElements

class MapData:
    """Read and write polygon data"""

    _shapefile_colnames = {
        'vegtype': OrderedDict(
             elmid='elmid',
             datum='datum',
             locatietype='loctype',
             vegtype_code='veg_code',
             vegtype_naam='veg_naam',
             vegtype_vorm='veg_vorm',
             vegtype_bedekkingcode='veg_bedcod',
             vegtype_bedekkingnum='veg_bednum',
             sbbcat_code='sbb_code',
             sbbcat_wetnaam='sbb_wetnm',
             sbbcat_nednaam='sbb_nednm',
             sbbcat_kortenaam='sbb_kortnm',
             sbbcat_vervangbaarheid='sbb_vevang',
             oppha='oppha',
             geometry='geometry',
        ),
        'mapspecies': OrderedDict(
            elmid='elmid',
            locatietype='loctype', 
            datum='datum', 
            sbbtype='sbbtype',
            krtsrt_srtcode='srtcode', 
            krtsrt_bedcode='bedcode', 
            krtsrt_aantalsklasse='aantkl',
            krtsrt_bednum='bednum', 
            cbs_srtwet='srtwet', 
            cbs_srtned='srtned',
            oppha='oppha', 
            geometry='geometry', 
        ),
        'pointspecies':OrderedDict(
            pntid='pntid', 
            pntloctype='loctype', 
            srtgroep='srtgroep', 
            srtnr='srtnr', 
            srtnednaam='nednaam',
            srtwetnaam='wetnaam', 
            srtsbbkl='sbbkl', 
            srttansley='tansley', 
            srtdatum='datum', 
            srtwrnmr='wrnmr',
            srtopm='opm', 
            xcr='xcr', 
            ycr='ycr', 
            geometry='geometry',
        )
    } # shapefile maximum column width is 10


    def __init__(self,maptables=None,polygons=None,lines=None):
        """MapPolygons constructor.


        Parameters
        ----------
        maptbl : DSreader.MapTables
            Map table data
        polygons : DSreader.MapElements
            Spatial data for all map polygons
        lines : DSreader.MapElelemnts
            Spatial data for all map lines


        """
        if maptables is None:
            maptables = dsr.MapTables()
        self._maptbl = maptables

        if polygons is None:
            polygons = dsr.MapElements()
        self._mapelements_polygons = polygons

        if lines is None:
            lines = dsr.MapElements()
        self._mapelements_lines = lines            
            
        self._maptblpath = self._maptbl._filepath
        self._polypath = self._mapelements_polygons._filepath
        self._linepath = self._mapelements_lines._filepath

        self._poly = self._mapelements_polygons.get_shape()
        self._poly = self._poly[['elmid','geometry']].copy()
        self._poly = self._poly.astype({'elmid':'str'})

        self._lines = self._mapelements_lines.get_shape()
        self._lines = self._lines[['elmid','geometry']].copy()
        self._lines = self._lines.astype({'elmid':'str'})

        self._poly['oppha']=self._poly['geometry'].area/10000


    def __repr__(self):
        return f'MapData (n={self._maptbl.__len__()})'

    @classmethod
    def from_filepaths(cls,mdbpath=None,polypath=None,linepath=None):
        """Create MapData instance from filepaths

        
        Parameters
        ----------
        mdbpath : str, optional
            Valid filepath for Microsoft Access mdb-file.
        polypath : str, optional
            Valid filepath to ESRI shapefile with vegetation polygons.
        linepath : str, optional
            Valid filepath to ESRI shapefile with vegetation lines.


        Returns
        -------
        MapData instance.
        
        
        """
        if isinstance(mdbpath,str):
            tables = MapTables.from_mdb(mdbpath)
        else:
            tables = MapTables()

        if isinstance(polypath,str):
            poly = MapElements.from_shapefile(polypath)
        else:
            poly = MapElements()

        if isinstance(linepath,str):
            line = MapElements.from_shapefile(linepath)
        else:
            line = MapElements()

        return cls(maptables=tables,polygons=poly,lines=line)


    def get_vegtype(self,element='v'):
        """
        Return mapped polygons with vegetation type
        
        
        Parameters
        ----------
        element : {'v','l'}, default ' v'
            Map element type.


        Returns
        -------
        pd.DataFrame


        """
        if element=='v':
            shape = self._poly
            shapepath = self._polypath
        if element=='l':
            shape = self._lines
            shapepath = self._linepath

        vegtbl = self._maptbl.get_vegtype()

        if vegtbl.empty:
            name = str(vegtbl)
            warnings.warn((f'Empty vegetation data in {name}'))
            return DataFrame()

        try:
            shape = pd.merge(shape,vegtbl,how='left',left_on='elmid',right_on='elmid',
                validate='one_to_many')
                
        except Exception as e:
            warnings.warn((f'Merge caused fatal exception: "{e}" '
                f'on shapefile {shapepath}" '
                f'and Access database "{self._maptblpath}"'))
            shape = DataFrame()

        else:
            shape = shape.dropna(subset=['locatietype'])

        return shape

    def get_mapspecies(self,element='v'):
        """Return map polygons with species data


        Parameters
        ----------
        element : {'v','l'}, default ' v'
            Map element type.

        Returns
        -------
        pd.DataFrame


        """
        if element=='v':
            shape = self._poly
        if element=='l':
            shape = self._lines
            
        mapspec = self._maptbl.get_mapspecies(loctype=element)

        mapspec = pd.merge(shape,mapspec,how='outer',left_on='elmid',
            right_on='elmid',validate='many_to_many')

        mapspec = mapspec.dropna(subset=['locatietype'])

        return mapspec


    def get_pointspecies(self):
        """Return species point data"""
        spc = self._maptbl.get_pointspecies()
        if not spc.empty:
            geometry = [Point(x,y) for x,y in zip(spc.xcr, spc.ycr)]
            spc = gpd.GeoDataFrame(spc,crs="EPSG:28992",geometry=geometry)

        return spc


    def to_shapefile(self,tablename=None,element='v',filepath=None):
        """Save table to ESRI shapefile

        Parameters
        ----------
        tablenamne : {'vegtype','mapspecies','pointspecies'}
            Kinde of table to save
        element : {'v','l'}
            map element type
        filepath : str
            Valid filepath for shapefile

        Returns
        -------
        pd.DataFrame

        Notes
        -----
        ESRI shapefile column names have a maximum length of ten
        characters and datetimes can not be saved, only dates.
        The returned value is the table that has been saved to 
        shapefile or it is an empty DataFrame.
        """
        # validate tablename
        tablenames = ['vegtype','mapspecies','pointspecies']
        if tablename not in tablenames:
            warnings.warn((f'{tablename} is not a valid tablename. '
                f'No file has been saved.'))
            return DataFrame()

        # validate element
        if element not in ['v','l']:
             warnings.warn((f'{element} is not a valid element type. '
                f'Elements of type "v" will be saved.'))           
             element='v'

        # validate filepath and correct
        dirname = os.path.dirname(filepath)
        if (dirname!='') and (not os.path.exists(dirname)):
            warnings.warn((f'{dirname} is not a valid directory. '
                f'No file has been saved.'))
            return DataFrame()
        if os.path.splitext(filepath)[1]=='':
            filepath = filepath+'.shp'
        if os.path.splitext(filepath)[1]!='.shp':
            filepath = os.path.splitext(filepath)[0]+'.shp'

        # get the right table 
        if tablename=='vegtype':
            table = self.get_vegtype(element=element)
        elif tablename=='mapspecies':
            table = self.get_mapspecies(element=element)
        elif tablename=='pointspecies':
            table = self.get_pointspecies()
        else:
            raise ValueError('{tablename} is not a valid table name.')

        if not table.empty:

            # rename columns
            table = table.rename(columns=self._shapefile_colnames[tablename])

            # date to string
            if 'datum' in table.columns: # shapefile has no datetime type
                all_strings = all((v is np.nan) or isinstance(v, str) 
                    for v in table['datum'])
                if all_strings:
                    table['datum'] = table['datum'].fillna('')
                else:
                    table['datum'] = table['datum'].apply(
                        lambda x: x.strftime(
                        '%d%m%Y') if not pd.isna(x) else '')

            # check if all columns are present
            shapecols = self._shapefile_colnames[tablename].values()
            coldif = set(table.columns)-set(shapecols)
            if len(coldif)!=0:
                warnings.warn((f'Unknown column names in table '
                    f'{tablename}: {coldif}.'))

            coldif2 = set(shapecols) - set(table.columns)
            if len(coldif2)!=0:
                warnings.warn((f'Missing column names in table '
                    f'{tablename}: {coldif2}.'))

            # order columns
            ordered_colnames = [colname for colname in shapecols
                if colname in table.columns] + list(coldif)
            table = table[ordered_colnames].copy()

            # save table
            table.to_file(filepath)

        return table
