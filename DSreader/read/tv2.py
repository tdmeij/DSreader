"""
Module with class Tv2 that reads a Turboveg2 dataset with releves 
from a folder with source files. 
   
""" 

from pathlib import Path
##import numpy as np
from pandas import DataFrame, Series
import pandas as pd
from geopandas import GeoDataFrame
import geopandas as gpd


class Tv2:
    """Read Turboveg2 dataset with vegetation releve data from folder."""

    TVABUND_COLS = ['RELEVE_NR','SPECIES_NR','COVER_CODE','LAYER',]

    TVHABITA_COLS = ['RELEVE_NR','REFERENCE','COVERSCALE',
        'PROJECT','AUTHOR','DATE','SYNTAXON','SURF_AREA','EXPOSITION',
        'INCLINATIO','COV_TOTAL','COV_TREES','COV_SHRUBS','COV_HERBS',
        'COV_MOSSES','COV_LICHEN','COV_ALGAE','COV_LITTER','TREE_HIGH',
        'TREE_LOW','SHRUB_HIGH','SHRUB_LOW','HERB_HIGH','HERB_LOW',
        'HERB_MAX','MOSS_IDENT','LICH_IDENT','REMARKS',]

    TVREMARKS_COLS = ['RELEVE_NR', 'REMARKS']

    TVWIN_COLS = ['FLORA', 'MINALLOW', 'MAXALLOW', 'MINACTUAL', 
        'MAXACTUAL', 'MAP', 'DICTIONARY', 'META']

    TVADMIN_COLS = ['RELEVE_NR', 'SOURCE_DB', 'GUID', 'CREAT_USER', 
        'CREAT_DATE', 'MOD_USER', 'MOD_DATE', 'NDFF_QUAL',]

    SBB_COLS = ['RELEVE_NR','REFERENCE','COVERSCALE','PROJECT',
        'AUTHOR','DATE','KM_HOK_X','KM_HOK_Y','BLOK','SYNTAXON',
        'NEW_SYNTAX','LENGTH','WIDTH','SURF_AREA','EXPOSITION',
        'INCLINATIO','COV_TOTAL','COV_TREES','COV_SHRUBS','COV_HERBS',
        'COV_MOSSES','COV_ALGAE','COV_LITTER','TREE_HIGH','TREE_LOW',
        'SHRUB_HIGH','SHRUB_LOW','HERB_HIGH','HERB_LOW','HERB_MAX',
        'MOSS_IDENT','PQ','TRANSECT','SBBCODE','REMARKS','BUREAU',
        'AUTEURNAAM','SBBPRJCODE','VELDNUMMER','LOC_TYPE','SBB_TYPE1',
        'SBB_TYPE2','DEELGEBIED','TOELICHTIN']

    LOCATION_COLUMNS = ['VELDNUMMER','LOC_TYPE','SBB_TYPE1','SBB_TYPE2',
        'DATE','COVERSCALE','SBBPRJCODE','KM_HOK_X','KM_HOK_Y',]

    TVHABITA_TYPES = {'RELEVE_NR': 'N','COUNTRY': 'C','REFERENCE': 'C',
        'TABLE_NR': 'C','NR_IN_TAB': 'C','COVERSCALE': 'C','PROJECT': 'C',
        'AUTHOR': 'C','DATE': 'C','SYNTAXON': 'C','SURF_AREA': 'N',
        'UTM': 'C','ALTITUDE': 'C','EXPOSITION': 'C','INCLINATIO': 'C',
        'COV_TOTAL': 'N','COV_TREES': 'N','COV_SHRUBS': 'N',
        'COV_HERBS': 'N','COV_MOSSES': 'N','COV_LICHEN': 'N',
        'COV_ALGAE': 'N','COV_LITTER': 'N','COV_WATER': 'N',
        'COV_ROCK': 'N','TREE_HIGH': 'N','TREE_LOW': 'N','SHRUB_HIGH': 'N',
        'SHRUB_LOW': 'N','HERB_HIGH': 'N','HERB_LOW': 'N','HERB_MAX': 'N',
        'CRYPT_HIGH': 'N','MOSS_IDENT': 'C','LICH_IDENT': 'C','REMARKS': 'C',}

    SBB_TYPES = {'AUTEURNAAM':'C','BED_OPENWA':'N','BLOK':'C','BUREAU':'C',
        'DEELGEBIED':'C','KM_HOK_X':'C','KM_HOK_Y':'C','LENGTH':'N',
        'LOC_TYPE':'C','NEW_SYNTAX':'C','PQ':'C','SBBCODE':'C','SBBPRJCODE':'C',
        'SBB_TYPE1':'C','SBB_TYPE2':'C','TOELICHTIN':'C','TRANSECT':'C',
        'VELDNUMMER':'C','WIDTH':'N',}

    COVERSCALES = {
        '00':'Procentueel',
        '01':'Braun/Blanquet',
        '02':'Braun/Blanquet (B,D&S)',
        '03':'Londo (1) volledig',
        '04':'Presentie/Absentie',
        '05':'Ordinale schaal',
        '06':'Barkman, Doing & Segal',
        '07':'Doing',
        '08':'4de Bosstatistiek',
        '09':'Londo (2) verkort',
        '10':'Barkman (ongepubl.)',
        '11':'Tansley',        
        '12':'Londo (decimaal)',
        '13':'Aantal indiv. (SBB)',
        '14':'Monitoringschaal',
        '15':'Domin',
        '16':'Hult-Sernander-DuRietz',
        '17':'Bos',
        '18':'Tansley Plus',
        '19':'Synoptische schaal',
        '20':'RWS-MD schaal',
        '21':'Maes schaal',
        '22':'CABO-schaal',
        '23':'RWS-RIZA schaal',
        '24':'Aq. terreinopn. schaal',
        }

    def __init__(self, folder, prjname=None):
        """
        Parameters
        ----------
        folder : str
            Valid path to folder with Tv2 files.
        prjname : str, optional
            User defined database project name.

        Notes
        -----
        In Turboveg2 stores releve data in a folder with several files:
            - tvhabita.dbf with header data.
            - tvabund.dbf with species abundance data.
            - remarks.dbf with longer releve remarks.
            - tvwin.set or tvwin.dbf with name of species dictionary.
            - tvadmin.dbf with project meta data (only in later versions).

        The file tvwin.set is a binary file that is not documented and 
        therefore hard to read. Only in later versions these data were 
        stored in a file called tvwin.dbf.
           
        """
        # set empty defaults
        self._tvhabita = DataFrame(columns=self.TVHABITA_COLS)
        self._tvabund = DataFrame(columns=self.TVABUND_COLS)
        self._remarks = DataFrame(columns=self.TVREMARKS_COLS)
        self._tvadmin = DataFrame(columns=self.TVADMIN_COLS)
        self._tvwin = DataFrame(columns=self.TVWIN_COLS)
        self._tvwinset = None
        self._flora = None
        self._map = None
        self._dictionary = None
        self.prjname = prjname

        # check path to source directory
        if not Path(folder).exists():
            raise ValueError((f'Could not find TV2 source directory '
                f'{folder}'))

        #raise ValueError((f'Not a valid Turboveg2 database '
        #    f'directory: {folder},'))

        # read dbf source files
        for filename in ['tvhabita','tvabund','remarks','tvadmin','tvwin']:

            fpath = Path(folder) / f'{filename}.dbf'
            if not fpath.is_file():
                continue

            gdf = gpd.read_file(fpath)
            table = DataFrame(gdf.drop(columns=['geometry']))

            if filename=='tvhabita':
                self._tvhabita = table.copy()

            if filename=='tvabund':
                self._tvabund = table.copy()

            if filename=='remarks':
                self._remarks = table.copy()

            if filename=='tvadmin':
                self._tvadmin = table.copy()

            if filename=='tvwin':
                self._tvwin = table.copy()
                if not self._tvwin.empty:
                    self._flora = self._tvwin.loc[0,'FLORA']
                    self._map = self._tvwin.loc[0,'MAP']
                    self._dictionary = self._tvwin.loc[0,'DICTIONARY']

        # read binary tvwin.set file
        fpath = Path(folder) / 'tvwin.set'
        if fpath.is_file():
            self._tvwinset = Path(fpath).read_bytes()
            # Decoding bytes takes some guessing.
            # Apperently '\x00' is just a null value.
            # So a list of line elements without nulls would be:
            tvwin_list = str(self._tvwinset).replace('x00','').split('\\')
            
            if self._flora is None:
                # get 4th item
                self._flora = tvwin_list[4]
            if self._map is None:
                # get 3th last item from list
                self._map = tvwin_list[-3]
            if self._dictionary is None:
                # get last item from list
                self._dictionary = tvwin_list[-1]


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


    @property
    def tvabund(self):
        """Return table of species abundance data."""
        tvabund = self._tvabund
        
        # add missing columns
        # Note: older versies lack column "LAYER", but do have a column
        # "COVER_PERC")
        for col in self.TVABUND_COLS:
            if col not in tvabund.columns:
                tvabund[col] = 0
        
        tvabund.sort_values(
            ['RELEVE_NR','LAYER','SPECIES_NR']
            ).reset_index(drop=True).copy()

        return tvabund[self.TVABUND_COLS]


    @property
    def tvhabita(self):
        """Return table of releve metadata."""
        return self._tvhabita.sort_values(['RELEVE_NR']).reset_index(drop=True)


    @property
    def remarks(self):
        """Return table of remarks."""

        """From Turbbove2 documentation:
        The total length of the remarks field covers a maximum of 1000 bytes. 
        However, the first 56 bytes is stored in the table TVHABITA.DBF, 
        and the remaining bytes are stored in the table REMARKS.DBF.
        
        The REMARKS field in TVHABITA.DBF is defined as
        REMARKS C 56 0.
        
        The REMARKS.dbf is defined  as
        RELEVE_NR    N    6  0    Relevé number (= system number)
        REMARKS      C    25 0    Remarks
        
        Therefore, the first 56 characters of a remark are stored in the
        REMARKS field of TVHABITA.dbf. The rest of the remark is split in 
        string of 25 charcters each and stored in REMARKS.dbf.
        """

        rem1 = self._tvhabita[['RELEVE_NR','REMARKS']].set_index('RELEVE_NR')
        rem2 = self._remarks

        for relid in rem1.index.values:
        
            # remark from TVHABITA
            rem = rem1.loc[relid,'REMARKS']

            # add rows from REMARKS.dbf
            remarks_table = rem2[rem2['RELEVE_NR']==relid]
            for substring in remarks_table['REMARKS'].values:
                rem += substring

            rem1.loc[relid,'REMARKS'] = rem

        rem1 = rem1.reset_index(drop=False).sort_values('RELEVE_NR')
        return rem1


    @property
    def years(self):
        """Years of releves."""
        allyears = list(self.tvhabita['DATE'].str[:4].unique())
        allyears = [year for year in allyears if year is not None]
        return allyears


    @property
    def usercols(self):
        """Names of user defined columns."""
        if self.tvhabita.empty:
            return []
        return [col for col in self.tvhabita.columns if col not in self.TVHABITA_COLS]


    @property
    def is_empty(self):
        """Return True if releve data are present."""
        return (self._tvhabita.empty) | (self._tvabund.empty)


    @property
    def has_sbbcols(self):
        """Contains all columns for a standard sbb database."""
        if self.is_empty:
            return False
        return all(col in self.tvhabita.columns for col in self.SBB_COLS)

    @property
    def flora(self):
        """Name of flora list."""
        return self._flora

    @property
    def dictionaries(self):
        """Name of lookuptable definitions."""
        return self._dictionary


    @property
    def locations(self):
        """Return geodataframe with releve locations."""

        if self.is_empty:
            cols = self.LOCATION_COLUMNS + ['geometry']
            gdf = gpd.GeoDataFrame(columns=cols, crs='EPSG:28992', geometry='geometry')
            return gdf
        
        # location data to dataframe
        colnames = [col for col in self.LOCATION_COLUMNS  
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
