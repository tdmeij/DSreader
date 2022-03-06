
"""
Module openshape contains class OpenShape for opening ESRI 
shapefiles to pandas GeoDataFrame. Shapefile errors that 
prevent GeoPandas from opening a shapefile are logged and
fixed as much as possible.
"""

import os
#from pathlib import Path
import pandas as pd
import geopandas as gpd
import fiona
import json
import warnings

class ReadPolyShape:
    """
    Open ESRI polygon shapefile as GeoPandas object

    Methods
    -------
    shape()
        Return GeoDataFrame
    error()
        Return open shape error message 
    columns()
        Return shapefile column names
    """

    _empty_error = {'class':None,'msg':None,'fpath':None}
    _bad_polygons = []

    def __init__(self,fpath,fix_errors=True):
        """
        Parameters
        ----------
        fpath : str
            filepath to ESRI shapefile
        fix_errors : bool, default True
            try to fix readerrors
        """
        self._fpath = fpath
        if not os.path.isfile(self._fpath):
            raise ValueError(f'{self._fpath} is not a valid filepath.')

        self._shape = self._readfile(self._fpath)
        if (self._shape is None) and (fix_errors==True) and (
            self._read_error is not None):
            self._shape = self._fix_errors()

        if (self._shape is None) and (self._read_error is not None):
            warnings.warn((f'Importerrrors cound not be fixed '
                f'on shapefile {self._fpath}.'))

        if self._shape is not None:
            self._shape.columns = map(str.lower,self._shape.columns)

    def __repr__(self):
        fname = os.path.basename(self._fpath)
        #shpname = os.path.splitext(fname)[0]
        nrows = len(self._shape)
        return f'{fname} (n={nrows})'

    def _readfile(self,fpath):
        """Read shapefile using standard GeoPandas read_file method"""
        self._read_error = None
        try:
            gdf = gpd.read_file(fpath)

        except Exception as e:
            self._read_error = (
                {'class':e.__class__,
                 'msg':repr(e),
                 'fpath':fpath,})
            gdf = None

        else:
            if not gdf.geom_type[0]=='Polygon':
                warnings.warn((f'Geometry type is {gdf.geom_type[0]} '
                    f'not "Polygon" on file {self._fpath}.'))
                gdf = None

        finally:
            return gdf

    def _fix_errors(self):

        err = self._read_error['msg']
        gdf = None

        # reconstruct missing shx index file
        if 'Set SHAPE_RESTORE_SHX config option to YES' in err:
            # .shx index files are automatically recalculated
            # by changing GDAL standard setting:
            fiona._env.set_gdal_config('SHAPE_RESTORE_SHX',True)
            # beware: now all .shx files are recreated, even when there not
            # missing or corrupted
            gdf = self._readfile(self._fpath)
            fiona._env.set_gdal_config('SHAPE_RESTORE_SHX',False)

        # try to fix linear ring error
        if 'A LinearRing must have at least 3 coordinate tuples' in err:
            self._fionashape = fiona.open(self._fpath)
            gdf = self._fix_linear_ring_error(self._fionashape)
            if gdf is not None:
                self._read_error = None

        return gdf


    def _fix_linear_ring_error(self,shapesource):
        """Return GeoDataFrame with a copy of all polygons except 
        polygons with less than three points"""

        # Fixes GeoPandas error message:
        # 'LinearRing must have at least 3 coordinate tuples'

        oldshape = list(shapesource)
        newshape = []
        for feature in oldshape:
        # feature is a dict with keys type,id,properties,geometry
            if feature["geometry"] is not None:
                geom = feature['geometry']
                coords = geom['coordinates']
                newcoords = []
                for poly in coords:

                    if len(poly)<3:
                        self._bad_polygons.append(
                            {'id':feature['id'],'length':len(poly)})
                        print(self._bad_polygons[-1])
                    else:
                        newcoords.append(poly)

                feature['geometry']['coordinates']=newcoords
            newshape.append(feature)

        # convert to geopandas
        dfnew = pd.DataFrame(newshape)
        jsongeom = json.loads(dfnew.to_json(orient='records'))
        gdf = gpd.GeoDataFrame.from_features(jsongeom)
        return gdf

    def shape(self):
        """Return shape as GeoPandas"""
        return self._shape

    def error(self):
        """Return error message as dict, returns None when no errors occured"""
        return self._read_error

    def columns(self):
        """Return shapefile column names as list"""
        return list(self._shape.columns)



