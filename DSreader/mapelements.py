
import warnings
from pandas import Series, DataFrame
import pandas as pd
import geopandas as gpd

from .read.readshapefile import ReadShapeFile

class MapElements:
    """Class MapElements holds spatial data for map elements  
    
    Methods
    -------
    get_shape : GeoDataFrame
        Return table of spatial data.
    get_colnames : list
        Return attribute column names.
    get_geomtype : str
        Return geometry type (vlakken or lines)
    get_filepath : str
        Return sourcefile path
    get_boundary : shape
        Return outer boundary of mappend area

    Classmethods
    ------------
    from_shapefile : MapElements
        Create MapElements instance from shapefilepath.
    """
    
    def __init__(self,shape=None,filepath=None):
        """MapElements constructor
        
        Parameters
        ----------
        shape : GeoDataFrame
            Spatial data
        filepath : str
            Sourcefile path (used for warnings)
            
        """
        if shape is None:
            shape = gpd.GeoDataFrame()
        self._shape = shape
        self._filepath = filepath

        if not self._shape.empty:
            self._geom_type = list(set(self._shape.geom_type))[0].lower()

            if self._shape.crs is None:
                self._shape = self._shape.set_crs('epsg:28992')


    def __repr__(self):
        return self._shape.__repr__()
        
    def __len__(self):
        return self._shape.__len__()

    def get_shape(self):
        """Return spatial data"""
        return self._shape
        
    def get_colnames(self):
        return list(self._shape)
        
    def get_geomtype(self):
        return self._geom_type
        
    def get_filepath(self):
        return self._filepath

    def get_boundary(self):
        """Return outer boundary of mapped area"""
        outline = self._shape.copy()
        outline['diss']=1
        outline = outline.dissolve('diss')
        outline = outline.geometry.boundary
        return outline
        

    @classmethod
    def from_shapefile(cls,filepath):
        """
        Create MapElements object from ESRI shapefile filepath."

        Parameters
        ----------
        filepath : str
            valid filepath to ESRI shapefile
        """

        if not isinstance(filepath,str):
            fptype = type(filepath)
            raise ValueError (f'Parameter filepath must be type "str" '
                f'not type {fptype}.')

        # open shapefile and check presence of column ElmID
        shp = ReadShapeFile(filepath)
        
        return cls(shape=shp._shape,filepath=filepath)
