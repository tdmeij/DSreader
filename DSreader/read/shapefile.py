
"""
Module openshape contains class OpenShape for opening ESRI 
shapefiles to pandas GeoDataFrame. Shapefile errors that 
prevent GeoPandas from opening a shapefile are logged and
fixed as much as possible.
"""

import os, sys, stat
import numpy as np
import pandas as pd
import geopandas as gpd
import fiona
import json
import warnings

class ShapeFile:
    """
    Open ESRI shapefile as GeoPandas object

    Attributes
    ----------
    shape
        Return shapefile data as GeoDataFrame.
    shape_errors
        Return table of errors in shapefile that have been fixed.
    columns
        Return list of shapefile column names.
    """

    _empty_error = {'class':None,'msg':None,'fpath':None}
    _bad_polygons = []

    def __init__(self,fpath):
        """
        Parameters
        ----------
        fpath : str
            filepath to ESRI shapefile

        Notes
        -----
        Geometry errors in shapefile are fixed as much as possible.
        Fixed errors can be retriwved with shape_errors()
        """
        self._fpath = fpath
        if not os.path.isfile(self._fpath):
            raise ValueError(f'{self._fpath} is not a valid filepath.')

        self._fname = os.path.basename(self._fpath)

        # empty dataframe for shape errors
        columns = ['fid','error','solution']
        self._shperr = pd.DataFrame(columns=columns)

        # read shapefile
        self._shape, self._shperr = self._readfile(self._fpath,self._shperr)

        """
        if (self._shape is None) and (fix_errors==True): 
            # there was a read error, try to fix it
            self._shape = self._fix_errors()
            if self._shape is None:
                warnings.warn((f'Importerrrors cound not be fixed '
                    f'on shapefile {self._fpath}.'))
        """

        if not self._shape.empty:
            self._shape.columns = map(str.lower,self._shape.columns)
            
            
            # get geometry type
            #self._geom_type = list(set(self._shape.geom_type))[0].lower()
            #self._geom_typeset = set(self._shape.geom_type)

    def __repr__(self):
        nrows = len(self._shape)
        return f'{self._fname} (n={nrows})'

    def _readfile(self,fpath,shperr):

        # reading shapefile with GeoPandas when .shx file is read only
        # gives a fiona drivererror:
        shxpath = f'{os.path.splitext(fpath)[0]}.shx'
        if os.path.exists(shxpath):
            if not os.access(shxpath, os.W_OK):
                os.chmod(shxpath, stat.S_IRWXU)
                warnings.warn((f'File permisson "read-only" has been set to '
                    f'"write" on shapefile index {shxpath}.'))

        # read shapefile with geopandas
        try:
            gdf = gpd.read_file(fpath)
            gdf.index.name = 'fid' #geopandas sets shapefile fid as index

        except Exception as e:

            self._gpd_read_err = {
                'class':e.__class__,
                'msg':repr(e),
                'fpath':fpath,
                }

            # try to fix geometry errors
            gdf, shperr = self.read_with_fiona(fpath,shperr)

        else:
            self._gpd_read_err = None
        
            # remove rows with None type geometries (GeoPandas does not 
            # check for this when reading a shapefile, but it's method 
            # geom.type will fail)
            ##if None in set(gdf.geom_type):
            ##    gdf, shape_errors = self.read_shape_with_errors(fpath)
            geom_null = gdf[gdf.geom_type.isnull()]
            if not geom_null.empty:
                warnings.warn((f'Deleted {len(geom_null)} rows without '
                    f'valid geometry in {self._fpath}.'))
                for fid,row in geom_null.iterrows():
                    idx = len(shperr)
                    shperr.loc[idx,'fid'] = fid
                    shperr.loc[idx,'error'] = f'Geometry type is None'
                    shperr.loc[idx,'solution'] =f'Dropped record with fid={fid}'
                gdf = gdf[gdf.geom_type.notnull()].copy()

        if gdf.empty:
            warnings.warn((f'Empty shapefile: {self._fpath}.'))

        return gdf,shperr

    def read_with_fiona(self,fpath,shperr=None):
        """Read shapefile with errors and return GeoPandas dataframe.

        Parameters
        ----------
        fpath : str
            Valid filepath to shapefile.

        Returns
        -------
        geoapndas.GeoDataFrame


        Notes
        -----
        This function is used internally, but it can be used with any 
        filepath without changes the status of the ShapeFile object. 
        Reading is done with fiona instead of geopandas and some errors 
        are fixed automatically and user warnings of changes are issued.
        """
        if shperr is None:
            shperr = self._shperr.copy()

        # open shapefile with fiona
        # .shx index files are automatically rebuild
        # by temprarily changing GDAL standard setting:
        with fiona.Env(SHAPE_RESTORE_SHX='YES'):
            self._fiona = fiona.open(fpath)

        # validate shape items one by one and copy valid items
        ##fiona_errors = []
        reclist = []
        for key in self._fiona.keys():

            # copy feature from fiona to dict
            feature = self._fiona.get(key)
            #fid = feature['id']
            #geom = feature['geometry']

            # error: Geometry is None
            if feature['geometry'] is None:
                idx = len(shperr)
                shperr.loc[idx,'fid'] = feature["id"]
                shperr.loc[idx,'error'] = f'Geometry type is None'
                shperr.loc[idx,'solution'] = f'Dropped record with fid={feature["id"]}'
                continue # simply ignore this feature

            # error: polygon field contains rings with less than three nodes
            if feature['geometry']['type']=='Polygon':
                newcoords = []
                badrings = 0
                for ring in feature['geometry']['coordinates']:
                    if len(ring)<3:
                        badrings+=1
                    else:
                        newcoords.append(ring)

                if badrings!=0:
                    
                    idx = len(shperr)
                    shperr.loc[idx,'fid'] = feature['id']
                    shperr.loc[idx,'error'] = f'Found {str(badrings)} polygon rings with less than three nodes.'
                    shperr.loc[idx,'solution'] = f'Dropped {str(badrings)} invalid polygon rings with less than three nodes'
        
                feature['geometry']['coordinates']=newcoords

            # append validated feature to reclist
            reclist.append(feature)
        
        # create GeoDataFrame from list of fiona features
        if self._fiona.crs.is_valid:
            crs = self._fiona.crs
        else:
            crs = shp._fiona.crs.from_epsg(28992) # dutch grid
        gdf = gpd.GeoDataFrame.from_features([feature for feature in reclist], crs=crs)

        # tidy up geodataframe
        columns = list(self._fiona.schema["properties"]) + ["geometry"]
        for col in columns:
            if col not in gdf.columns: # fiona drops columns with only nans?
                gdf[col] = np.nan
        gdf = gdf[columns]  
        gdf.index.name = 'fid' #geopandas sets shapefile fid as index

        return gdf, shperr

    @property
    def shape(self):
        """Return shape as GeoPandas dataframe"""
        return self._shape

    @property
    def shape_errors(self):
        """Return Pandas dataframe with polygon errors."""
        return self._shape_errors

    @property
    def columns(self):
        """Return shapefile column names as list"""
        return list(self._shape.columns)

    @property
    def filepath(self):
        """Return shapefilepath"""
        return self._fpath
