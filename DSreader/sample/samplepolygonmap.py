"""
Module with class SampleShape for sampling polygon maps with a regular 
grid.
"""
import numpy as np
from pandas import Series, DataFrame
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

class SamplePolygonMap:
    """Sample polygon map at grid points.
    
    Methods
    -------
    gridpoints
        GeoDataFrame with gridpoints.
    sample
        GeoDataFrame with sampled values at gridpoints.
    """

    XMIN = 188000
    XMAX = 276000
    YMIN = 307000
    YMAX = 609000

    def __init__(self,polygonmap,bbox=None,gridtype='regular',
        step=100,crs='epsg:28992',):
        """
        Parameters
        ----------
        polygomap : geopandas.GeoDataFrame
            Polygon map which must be sampled.
        bbox : numpy array, list or tuple, optional.
            Grid limits as (xmin,ymin,xmax,ymax).
        gridtype : {'regular','repr'}, default 'regular'
            Sample grid layout.
        step : number, default 100
            Grid points distance for regular grid.
        crs : str, default 'epsg:28992'
            Polygon map crs.
        """

        if not isinstance(polygons,gpd.geodataframe.GeoDataFrame):
            raise Exception(f'Expect class GeoDataFrame, not {shape.__class__}')

        self._poly = polygons
        self._step = step
        self._crs = crs

        if bbox is None:
            self._bbox = self._map_bounds()
        elif isinstance(bbox,gpd.geodataframe.GeoDataFrame):
            self._bbox = self._map_bounds(bbox)
            #self._bbox = bbox.total_bounds
        elif len(list(bbox))==4:
            self._bbox = bbox
        else:
            raise ValueError(f'Invalid bbox {bbox}')

        if gridtype not in ['regular','repr']:
            warnings.warn((f'{gridtype} is not a valid grid type. '
                f'Regular grid will be returned.'))
            self._gridtype='regular'

        if gridtype=='regular':
            self._gridpoints = self._regular_grid()
        elif gridtype=='repr':
            self._gridpoints = self._poly.representative_point()
        self._gridpoints = self._gridpoints.reset_index(drop=True)

        self._sample = gpd.sjoin(self._gridpoints,self._poly,how='inner',op='within')
        self._sample = self._sample.reset_index(drop=True)
        if 'index_right' in self._sample.columns:
            self._sample = self._sample.drop(columns=['index_right'])


    def __repr__(self):
        npoly = len(self._poly)
        return f'{self.__class__.__name__} ({npoly} polygons)'       

    def _map_bounds(self,polymap=None):
        """Return boundary points for a regular sample grid that covers 
        entire polygon shape
               
        Returns
        -------
        numpy.array([xmin,ymin,xmax,ymax])
           
        """
        if polymap is None:
            polymap = self._poly

        xmin,ymin,xmax,ymax = polymap.total_bounds
        step = self._step
        xmin = xmin - (xmin % step)
        xmax = xmax - (xmax % step) + step
        ymin = ymin - (ymin % step)
        ymax = ymax - (ymax % step) + step
        return np.array([xmin,ymin,xmax,ymax])

    def _regular_grid(self):
        """Return regular grid of sampling points"""
        xmin,ymin,xmax,ymax = self.bbox
        xp = np.arange(xmin,xmax,self._step)
        yp = np.arange(ymin,ymax,self._step)
        xx, yy = np.meshgrid(xp, yp)
        pointgeom = gpd.points_from_xy(xx.flatten(), yy.flatten(), crs=self._crs)
        gridpoints = gpd.GeoDataFrame(geometry=pointgeom)
        gridpoints['area_ha'] = self._step**2/10000
        return gridpoints

    @property
    def gridpoints(self):
        """GeoDataFrame with gridpoints."""
        return self._gridpoints

    @property
    def sample(self):
        """GeoDataFrame with sampled values at gridpoints."""
        return self._sample

    @property
    def bbox(self):
        """Return grid boundaries as (xmin,ymin,xmax,ymax)"""
        return self._bbox

    def plot_sample(self):
        """Plot map of gridpoints and sampled points"""
        fig, ax = plt.subplots()
        self.gridpoints.plot(ax=ax,color='#c0d6e4',markersize=1)
        self.sample.plot(ax=ax,color='#9000c0',markersize=5)
        plt.xticks(rotation=90)
        return ax