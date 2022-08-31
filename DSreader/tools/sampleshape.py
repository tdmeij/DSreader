"""
Module with class SampleShape for sampling polygon maps with a regular 
grid.
"""
import numpy as np
from pandas import Series, DataFrame
import pandas as pd
import geopandas as gpd

class SampleShape:
    """Create regular grid and sample polygon map at grid points"""

    XMIN = 188000
    XMAX = 276000
    YMIN = 307000
    YMAX = 609000

    def __init__(self,polygons,gridbounds=None,gridtype='regular',
        step=100,crs='epsg:28992',):
        """
        Parameters
        ----------
        polygons : geopandas.GeoDataFrame
            Polygon map.
        gridbounds : numpy array, list or tuple, optional.
            Grid limits as (xmin,ymin,xmax,ymax).
        gridtype : {'regular','repr'}, default 'regular'
            Sample grid type.
        step : number, default 100
            Regular grid points interval.
        crs : str, default 'epsg:28992'
            polygon map crs  
        """

        if not isinstance(polygons,gpd.geodataframe.GeoDataFrame):
            raise Exception(f'Expect class GeoDataFrame, not {shape.__class__}')
        self._poly = polygons

        self._step = step
        self._crs = crs

        if gridbounds is None:
            self._gridbounds = self._bounds()

        if gridtype not in ['regular','repr']:
            warnings.warn((f'{gridtype} is not a valid grid type. '
                f'Regular grid will be returned.'))
            self._gridtype='regular'

        if gridtype=='regular':
            self._gridpoints = self._regular_grid()
        if gridtype=='repr':
            self._gridpoints = self._poly.representative_point()
        self._gridpoints = self._gridpoints.reset_index(drop=True)

        self._sample = gpd.sjoin(self._gridpoints,self._poly,how='inner',op='within')
        self._sample = self._sample.reset_index(drop=True)
        if 'index_right' in self._sample.columns:
            self._sample = self._sample.drop(columns=['index_right'])


    def __repr__(self):
        npoly = len(self._poly)
        return f'{self.__class__.__name__} ({npoly} polygons)'       

    def _bounds(self):
        """Return boundary points for a regular sample grid that covers 
        entire polygon shape
               
        Returns
        -------
        numpy.array([xmin,ymin,xmax,ymax])
           
        """
        step = self._step
        xmin,ymin,xmax,ymax = self._poly.total_bounds
        xmin = xmin - (xmin % step)
        xmax = xmax - (xmax % step) + step
        ymin = ymin - (ymin % step)
        ymax = ymax - (ymax % step) + step
        return np.array([xmin,ymin,xmax,ymax])

    def _regular_grid(self):
        """Return regular grid of sampling points"""
        xmin,ymin,xmax,ymax = self._gridbounds
        xp = np.arange(xmin,xmax,self._step)
        yp = np.arange(ymin,ymax,self._step)
        xx, yy = np.meshgrid(xp, yp)
        pointgeom = gpd.points_from_xy(xx.flatten(), yy.flatten(), crs=self._crs)
        gridpoints = gpd.GeoDataFrame(geometry=pointgeom)
        gridpoints['area_ha'] = self._step**2/10000
        return gridpoints

    def gridpoints(self):
        """Return geodataframe with gridpoints"""
        return self._gridpoints


    def sample(self):
        """
        Return gridpoints with polygon sample values
        """
        return self._sample
