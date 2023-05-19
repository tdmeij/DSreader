"""
Module with class SampleShape for sampling polygon maps with a regular 
grid.
"""
import numpy as np
from pandas import Series, DataFrame
import pandas as pd
from geopandas import GeoDataFrame
import geopandas as gpd
import matplotlib.pyplot as plt

class SamplePolygonMap:
    """Sample polygon map at grid points.

    Properties
    ----------
    gridpoints
        GeoDataFrame with gridpoints.
    sample
        GeoDataFrame with sampled values at gridpoints.
    bbox
        Grid boundaries as (xmin,ymin,xmax,ymax).

    Methods
    -------
    plot_sample
        Plot map of sample points.

    """

    XMIN = 0
    XMAX = 280000
    YMIN = 300000
    YMAX = 620000
    STEP = 100
    CRS = 'epsg:28992' # Dutch RD grid

    def __init__(self,polygonmap,bbox=None,gridtype='regular',
        step=100,grid=None,crs='epsg:28992',):
        """
        Parameters
        ----------
        polygonmap : geopandas.GeoDataFrame
            Polygon map as input to sample.
        bbox : numpy array, list or tuple, optional.
            Grid limits as (xmin,ymin,xmax,ymax).
        gridtype : {'regular','repr'}, default 'regular'
            Sample grid layout.
        step : number, default 100
            Grid points distance for regular grid.
        grid : GeoDataFrame, optional
            Existing grid for sampling (gridtype and step will be
            ignored).
        crs : str, default 'epsg:28992'
            Polygon map crs.

        
        """

        if not isinstance(polygonmap,GeoDataFrame):
            raise Exception(f'Expect class GeoDataFrame, not {polygonmap.__class__}')

        self._poly = polygonmap
        self._step = step
        self._crs = crs

        if bbox is None:
            self._bbox = self._map_bounds()
        elif isinstance(bbox,GeoDataFrame):
            self._bbox = self._map_bounds(bbox)
            #self._bbox = bbox.total_bounds
        elif len(list(bbox))==4:
            self._bbox = bbox
        else:
            raise ValueError(f'Invalid bbox {bbox}')

        # Set grid or define new grid
        if grid is not None:

            if not isinstance(grid,GeoDataFrame):
                warnings.warn((f'Given grid is not GeoPandas but '
                    f'{type(grid)}. New default grid will be created.'))
                grid = None
            self._gridpoints = grid

        if grid is None:
        
            if gridtype not in ['regular','repr']:
                warnings.warn((f'{gridtype} is not a valid grid type. '
                    f'Regular grid will be returned.'))
                self._gridtype='regular'

            if gridtype=='regular':
                self._gridpoints = self._regular_grid()
            elif gridtype=='repr':
                self._gridpoints = self._poly.representative_point()
            self._gridpoints = self._gridpoints.reset_index(drop=True)
        
        # Sample the polygon on gridpoints
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
        gridpoints = self.regular_grid(bbox=self.bbox,step=self._step)
        return gridpoints

    @classmethod
    def regular_grid(cls, bbox=None, step=None):

        # set grid bounadries
        if bbox is None: # nederland
            xmin,ymin,xmax,ymax = cls.XMIN,cls.YMIN,cls.XMAX,cls.YMAX
        else:
            xmin,ymin,xmax,ymax = bbox

        # set grid distance
        if step is None:
            step = cls.STEP

        xp = np.arange(xmin,xmax,step)
        yp = np.arange(ymin,ymax,step)
        xx, yy = np.meshgrid(xp, yp)
        pointgeom = gpd.points_from_xy(xx.flatten(), yy.flatten(), crs=cls.CRS)
        gridpoints = gpd.GeoDataFrame(geometry=pointgeom)
        gridpoints['pointid'] = gridpoints.index.astype(str)
        gridpoints['pointarea_ha'] = step**2/10000

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