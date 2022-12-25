
"""
Module openshape contains class OpenShape for opening ESRI 
shapefiles to pandas GeoDataFrame. Shapefile errors that 
prevent GeoPandas from opening a shapefile are logged and
fixed as much as possible.
"""

import os, sys, stat
import pandas as pd
import geopandas as gpd
import fiona
import json
import warnings

class ReadShapeFile:
    """
    Open ESRI shapefile as GeoPandas object

    Methods
    -------
    shape()
        Return shapefile data as GeoDataFrame.
    shape_errors()
        Return table of errors in shapefile that have been fixed.
    columns()
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

        # read shapefile
        self._shape,self._shape_errors = self._readfile(self._fpath)

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
            self._geom_type = list(set(self._shape.geom_type))[0].lower()
            self._geom_typeset = set(self._shape.geom_type)



    def __repr__(self):
        nrows = len(self._shape)
        return f'{self._fname} (n={nrows})'

    def _readfile(self,fpath):


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
            shape_errors = pd.DataFrame()

        except Exception as e:

            self._gpd_read_err = {
                'class':e.__class__,
                'msg':repr(e),
                'fpath':fpath,
                }

            # try to fix geometry errors
            gdf, shape_errors = self._read_shape_with_errors(fpath)

        else:
            self._gpd_read_err = None
        
            # check for None type geometries (GeoPandas does not check
            # for this when reading a shapefile, but it's method geom.type
            # will fail)
            if None in set(gdf.geom_type):
                gdf, shape_errors = self._read_shape_with_errors(fpath)

        if gdf.empty:
            warnings.warn((f'Empty shapefile: {self._fpath}.'))

        return gdf,shape_errors

    def _read_shape_with_errors(self,fpath):

        fiona_errors = []
        reclist = []

        # open shapefile with fiona
        # .shx index files are automatically rebuild
        # by changing GDAL standard setting:
        #fiona._env.set_gdal_config('SHAPE_RESTORE_SHX',True)
        # beware: now all .shx files are recreated, even when there not
        # missing or corrupted
        #####gdf = self._readfile(self._fpath)
        self._fiona = fiona.open(fpath)
        #fiona._env.set_gdal_config('SHAPE_RESTORE_SHX',False)    

        # validate shape items one by one and copy valid items
        for key in self._fiona.keys():

            # copy feature from fiona to dict
            feature = self._fiona.get(key)
            fid = feature['id']
            geom = feature['geometry']

            # error: Geometry is None
            if geom is None:
                fiona_errors.append({
                    'fid':fid,
                    'geomtype':'None',
                    'error':f'Geometry type is None',
                    #'fpath':self._fiona.path,
                    })
                continue # simply ignore this feature

            # error: polygon field contains rings with less than three nodes
            if geom['type']=='Polygon':
                newcoords = []
                badrings = 0
                for ring in geom['coordinates']:
                    if len(ring)<3:
                        badrings+=1
                    else:
                        newcoords.append(ring)

                if badrings!=0:
                    fiona_errors.append({
                        'fid':fid,
                        'geomtype': geom['type'],
                        'error':f'Dropped rings with less than three nodes',
                        #'fpath':self._fiona.path,
                        })
        
                feature['geometry']['coordinates']=newcoords

            # append validated feature to reclist
            reclist.append(feature)
        

        # create GeoDataFrame from fiona reclist
        df = pd.DataFrame(reclist)
        jsongeom = json.loads(df.to_json(orient='records'))
        gdf = gpd.GeoDataFrame.from_features(jsongeom)
        gdf.index.name = 'fid' #geopandas sets shapefile fid as index

        errors = pd.DataFrame(fiona_errors)

        return gdf,errors

    def shape(self):
        """Return shape as GeoPandas dataframe"""
        return self._shape

    def shape_errors(self):
        """Return Pandas dataframe with polygon errors."""
        return self._shape_errors

    def columns(self):
        """Return shapefile column names as list"""
        return list(self._shape.columns)

    def filepath(self):
        """Return shapefilepath"""
        return self._fpath
