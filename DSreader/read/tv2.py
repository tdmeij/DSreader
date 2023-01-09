
from pathlib import Path
from pandas import DataFrame, Series
import pandas as pd
from geopandas import GeoDataFrame
import geopandas as gpd


class Tv2:
    """Read Turboveg2 dataset with vegetation releves."""

    TVABUND_COLS = ['RELEVE_NR','SPECIES_NR','COVER_CODE','LAYER']

    TVHABITA_COLS_STANDARD = ['RELEVE_NR','REFERENCE','COVERSCALE',
        'PROJECT','AUTHOR','DATE','SYNTAXON','SURF_AREA','EXPOSITION',
        'INCLINATIO','COV_TOTAL','COV_TREES','COV_SHRUBS','COV_HERBS',
        'COV_MOSSES','COV_LICHEN','COV_ALGAE','COV_LITTER','TREE_HIGH',
        'TREE_LOW','SHRUB_HIGH','SHRUB_LOW','HERB_HIGH','HERB_LOW',
        'HERB_MAX','MOSS_IDENT','LICH_IDENT','REMARKS']

    TVREMARKS_COLS = ['RELEVE_NR', 'REMARKS']

    STANDARD_COLS_SBB = ['RELEVE_NR','REFERENCE','COVERSCALE','PROJECT',
        'AUTHOR','DATE','KM_HOK_X','KM_HOK_Y','BLOK','SYNTAXON',
        'NEW_SYNTAX','LENGTH','WIDTH','SURF_AREA','EXPOSITION',
        'INCLINATIO','COV_TOTAL','COV_TREES','COV_SHRUBS','COV_HERBS',
        'COV_MOSSES','COV_ALGAE','COV_LITTER','TREE_HIGH','TREE_LOW',
        'SHRUB_HIGH','SHRUB_LOW','HERB_HIGH','HERB_LOW','HERB_MAX',
        'MOSS_IDENT','PQ','TRANSECT','SBBCODE','REMARKS','BUREAU',
        'AUTEURNAAM','SBBPRJCODE','VELDNUMMER','LOC_TYPE','SBB_TYPE1',
        'SBB_TYPE2','DEELGEBIED','TOELICHTIN']

    LOCATIONS_COLUMNS = ['VELDNUMMER','LOC_TYPE','SBB_TYPE1','SBB_TYPE2',
        'DATE','COVERSCALE','SBBPRJCODE','KM_HOK_X','KM_HOK_Y',]

    STANDARD_TYPES = {'RELEVE_NR': 'N','COUNTRY': 'C','REFERENCE': 'C',
        'TABLE_NR': 'C','NR_IN_TAB': 'C','COVERSCALE': 'C','PROJECT': 'C',
        'AUTHOR': 'C','DATE': 'C','SYNTAXON': 'C','SURF_AREA': 'N',
        'UTM': 'C','ALTITUDE': 'C','EXPOSITION': 'C','INCLINATIO': 'C',
        'COV_TOTAL': 'N','COV_TREES': 'N','COV_SHRUBS': 'N',
        'COV_HERBS': 'N','COV_MOSSES': 'N','COV_LICHEN': 'N',
        'COV_ALGAE': 'N','COV_LITTER': 'N','COV_WATER': 'N',
        'COV_ROCK': 'N','TREE_HIGH': 'N','TREE_LOW': 'N','SHRUB_HIGH': 'N',
        'SHRUB_LOW': 'N','HERB_HIGH': 'N','HERB_LOW': 'N','HERB_MAX': 'N',
        'CRYPT_HIGH': 'N','MOSS_IDENT': 'C','LICH_IDENT': 'C','REMARKS': 'C'}

    SBB_TYPES = {'AUTEURNAAM':'C','BED_OPENWA':'N','BLOK':'C','BUREAU':'C',
        'DEELGEBIED':'C','KM_HOK_X':'C','KM_HOK_Y':'C','LENGTH':'N',
        'LOC_TYPE':'C','NEW_SYNTAX':'C','PQ':'C','SBBCODE':'C','SBBPRJCODE':'C',
        'SBB_TYPE1':'C','SBB_TYPE2':'C','TOELICHTIN':'C','TRANSECT':'C',
        'VELDNUMMER':'C','WIDTH':'N',}

    COVERSCALES = {
        '00':'Procentueel','01':'Braun/Blanquet',
        '02':'Braun/Blanquet (B,D&S)','03':'Londo (1) volledig',
        '04':'Presentie/Absentie','05':'Ordinale schaal',
        '06':'Barkman, Doing & Segal','07':'Doing',
        '08':'4de Bosstatistiek','09':'Londo (2) verkort',
        '10':'Barkman (ongepubl.)','11':'Tansley',        
        '12':'Londo (decimaal)','13':'Aantal indiv. (SBB)',
        '14':'Monitoringschaal','15':'Domin',
        '16':'Hult-Sernander-DuRietz','17':'Bos',
        '18':'Tansley Plus','19':'Synoptische schaal',
        '20':'RWS-MD schaal','21':'Maes schaal','22':'CABO-schaal',
        '23':'RWS-RIZA schaal','24':'Aq. terreinopn. schaal',
        }

    def __init__(self, tvhabita=None, tvabund=None, remarks=None,
        tvadmin=None, tvwin=None, prjname=None):
        """
        Parameters
        ----------
        tvhabita : DataFrame
            Turboveg2 table with header data.
        tvabund : DataFrame
            Turboveg2 table with species abundance data.
        remarks : DataFrame
            Turboveg2 table with releve remarks.
        tvadmin : DataFrame
            Turboveg2 admnin table.
        tvwin : DataFrame
            Turboveg2 tvwin table with metadata.
        prjname :str
            User defined project name.
        """

        if tvhabita is None:
            tvhabita = DataFrame(columns=self.TVHABITA_COLS_STANDARD)
        self._tvhabita = tvhabita

        if tvabund is None:
            tvabund = DataFrame(columns=self.TVABUND_COLS)
        self._tvabund = tvabund

        if remarks is None:
            remarks = DataFrame(columns=self.TVREMARKS_COLS)
        self._remarks = remarks

        self._tvadmin = tvadmin
        self._tvwin = tvwin
        self.prjname = prjname
        

    def __repr__(self):
        if self.prjname is None:
            return f'{self.__class__.__name__} (n={len(self)})'
        else:
            return f'{self.prjname} (n={self.__len__()})'


    def __len__(self):
        if self._tvhabita is not None:
            return len(self._tvhabita)
        else:
            return 0


    @classmethod
    def from_folder(cls,folder,prjname=None):
        """Read Turboveg2 database from folder.

        Parameters
        ----------
        folder : str
            Valid filepath to folder with dbf files.
        tvname : str
            User defined database project name.

        Returns
        -------
        Instance of classe TV2

        Notes
        -----
        A Turboveg2 database with releves consists of a folder with
        at least the following three dbf files: tvhabita.dbf, tvabund.dbf
        and remarks.dbf. Index files with extension .cdx are usually 
        present but not nessesary for reading data.
        """

        if not Path(folder).exists():
            raise ValueError((f'Not a valid Turboveg2 database '
                f'directory: {folder},'))

        tablenames = ['tvhabita','tvabund','remarks','tvadmin','tvwin']

        tables = {}
        for name in tablenames:
            fpath = Path(folder) / f'{name}.dbf'
            tables[name] = DataFrame()
            if fpath.exists():
                gdf = gpd.read_file(fpath)
                tables[name] = DataFrame(gdf.drop(columns=['geometry']))

        return cls(tvhabita=tables['tvhabita'],tvabund=tables['tvabund'],
            remarks=tables['remarks'],tvadmin=tables['tvadmin'],
            tvwin=tables['tvwin'],prjname=prjname)


    @property
    def tvabund(self):
        tvabund = self._tvabund.sort_values(
            ['RELEVE_NR','LAYER','SPECIES_NR']
            ).reset_index(drop=True).copy()
        return tvabund


    @property
    def tvhabita(self):
        """Return table of releve metadata."""
        return self._tvhabita.sort_values(['RELEVE_NR']).reset_index(drop=True)


    @property
    def years(self):
        """Years of releves."""
        
        allyears = list(self.tvhabita['DATE'].str[:4].unique())
        allyears = [year for year in allyears if year is not None]
        return allyears


    @property
    def usercols(self):
        """Names of user defined columns."""
        if self.get_tvhabita().empty:
            return []
        return [col for col in self.tvhabita.columns if col not in self.STANDARD_TV2COLS]


    @property
    def is_empty(self):
        """Return True if releve data are present."""
        return (self._tvhabita.empty) | (self._tvabund.empty)


    @property
    def contains_sbbcols(self):
        """Contains all columns for a standard sbb database."""
        if self.is_empty:
            return False            
        return all(col in self.tvhabita.columns for col in self.STANDARD_COLS_SBB)


    def get_locations(self):
        """Return geodataframe with releve locations."""
        
        if self.is_empty:
            cols = self.LOCATIONS_COLUMNS + ['geometry']
            gdf = gpd.GeoDataFrame(columns=cols, crs='EPSG:28992', geometry='geometry')
            return gdf
        
        # location data to dataframe
        colnames = [col for col in self.LOCATIONS_COLUMNS  
            if col in self.tvhabita.columns]
        tvhab = self.tvhabita[colnames].copy()

        # modify columns
        tvhab['COVERSCALE'] = tvhab['COVERSCALE'].replace(self.COVERSCALES)
        xcr = tvhab['KM_HOK_X']*1000
        ycr = tvhab['KM_HOK_Y']*1000
        tvhab = tvhab.drop(columns=['KM_HOK_X','KM_HOK_Y'])
        tvhab.columns = map(str.lower,tvhab.columns)

        #create geodataframe
        geom = gpd.points_from_xy(xcr,ycr)
        gdf = gpd.GeoDataFrame(tvhab,geometry=geom,crs='EPSG:28992')
        return gdf
