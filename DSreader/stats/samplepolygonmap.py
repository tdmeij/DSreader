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
    
    Examples
    --------
    smp = SamplePolygonMap(polygonmap)
    sample = smp.get_polygon_sample()
    smp.plot_sample()
            
    """

    XMIN = 0
    XMAX = 280000
    YMIN = 300000
    YMAX = 620000
    GRIDSTEP = 100
    CRS = 'epsg:28992' # Dutch RD grid
    GRIDPOINTS_COLOR = '#c0d6e4'
    DATAPOINTS_COLOR = '#9000c0'


    def __init__(self, polygonmap, gridtype='regular', step=100, 
        samplegrid=None, crs='epsg:28992',):
        """
        Parameters
        ----------
        polygonmap : geopandas.GeoDataFrame
            Polygon map as input to sample.
        gridtype : {'regular','repr'}, default 'regular'
            Sample grid layout.
        step : number, default 100
            Grid points distance for regular grid.
        samplegrid : GeoDataFrame, optional
            Existing grid for sampling (parameters gridtype and step 
            will be ignored).
        crs : str, default 'epsg:28992'
            Polygon map crs.

        
        """

        if not isinstance(polygonmap, GeoDataFrame):
            raise Exception(f'Expect class GeoDataFrame, not {polygonmap.__class__}')

        if samplegrid is not None:
            if not isinstance(samplegrid,GeoDataFrame):
                warnings.warn((f'Given grid is not GeoPandas but '
                    f'{type(samplegrid)}. New default grid will be created.'))
                samplegrid = None

        # set variables
        self._polygonmap = polygonmap
        self._gridtype = gridtype
        self._step = step
        self._samplegrid = samplegrid
        self._crs = crs

    def __repr__(self):
        polygon_count = len(self._polygonmap)
        return f'{self.__class__.__name__} ({polygon_count} polygons)'

    @classmethod
    def create_gridbounds(cls, shape, step=None):
        """Return regular sampling grid boundary points.
        
        Parameters
        ----------
        shape : GeoDataFrame
            Valid polygon shape.
        step : int, optional
            Distance between grid points.            

        Returns
        -------
        dictionary
            {'xmin':xmin, 'ymin':ymin, 'xmax':xmax, 'ymax':ymax}
        """
        ##if shape is None:
        ##    raise ValueError((f'Polygon shape must be given.'))

        if step is None:
            step = cls.GRIDSTEP

        # get sampling grid bounds
        xmin, ymin, xmax, ymax = shape.total_bounds
        xmin = xmin - (xmin % step)
        xmax = xmax - (xmax % step) + step
        ymin = ymin - (ymin % step)
        ymax = ymax - (ymax % step) + step

        return {'xmin':xmin, 'ymin':ymin, 'xmax':xmax, 'ymax':ymax}


    @classmethod
    def create_sampling_grid(cls, polyshape, gridtype='regular', step=None):
        """Return sampling grid for polgon shape.
        
        Parameters
        ----------
        polyshape : geopandas.GeoDataFrame
            Polygons that will be sampled.
         gridtype : {'regular','repr'}, default 'regular'
            Sample grid layout.    
         step : int, optional
            Distance between grid points for a regular grid.

        Returns
        -------
        geopandas.GeoDataFrame
            Grid of sampling points.
        """

        if gridtype not in ['regular','repr']:
            warnings.warn((f'{gridtype} is not a valid grid type. '
                f'Regular grid will be returned.'))
            gridtype='regular'

        if step is None:
            step = cls.GRIDSTEP

        if gridtype=='regular':
            gridbounds = cls.create_gridbounds(shape=polyshape, 
                step=step)
            gridpoints = cls.create_regular_grid(
                step=step, 
                xmin=gridbounds['xmin'], 
                xmax=gridbounds['xmax'], 
                ymin=gridbounds['ymin'], 
                ymax=gridbounds['ymax']
            )

        if gridtype=='repr':
            gridpoints = polyshape.representative_point()

        return gridpoints.reset_index(drop=True)


    @classmethod
    def create_regular_grid(cls, step=None, xmin=None, xmax=None, ymin=None, ymax=None):
        """Return regular grid of sampling points.

        Parameters
        ----------
        step : float, default GRIDSTEP
            Distance between grid points.
        xmin : float, optional
            Grid left boundary.
        xmax : float, optional
            Grid right boundary.
        ymin : float, optional
            Grid lower boundary.
        ymax : float, optional
            Grid upper boundary.

        Returns
        -------
        geopandas.GeoDataFrame
        
        Notes
        -----
        If no boundaries are given, a grid covering the Netherlands 
        is returned.
            
        """

        # default grid bounadries
        if any([xmin, ymin, xmax, ymax]):
            xmin, ymin, xmax, ymax = cls.XMIN, cls.YMIN, cls.XMAX, cls.YMAX

        # default grid distance
        if step is None:
            step = cls.STEP

        # create grid of regular points
        xp = np.arange(xmin, xmax, step)
        yp = np.arange(ymin, ymax, step)
        xx, yy = np.meshgrid(xp, yp)
        pointgeom = gpd.points_from_xy(xx.flatten(), yy.flatten(), crs=cls.CRS)
        gridpoints = gpd.GeoDataFrame(geometry=pointgeom)

        # add columns with pointid and area
        gridpoints['pointid'] = gridpoints.index.astype(str)
        gridpoints['pointarea_ha'] = step**2/10000

        return gridpoints

    @property
    def grid(self):
        """GeoDataFrame with gridpoints."""

        if self._samplegrid is None:

            step = self._step
            if step is None:
                step = self.GRIDSTEP

            self._samplegrid = self.create_sampling_grid(self._polygonmap, 
                gridtype=self._gridtype, step=step)

        return self._samplegrid

    @property
    def polygons(self):
        """Return polgon map."""
        return self._polygonmap


    def get_polygon_sample(self):
        """Return GeoDataFrame with sampled values at gridpoints."""
        sample = gpd.sjoin(self.grid, self.polygons, how='inner', predicate='within')

        if 'index_right' in sample.columns:
            sample = sample.drop(columns=['index_right'])

        return sample.reset_index(drop=True)


    def plot_sample(self):
        """Plot sampled gridpoints and return ax"""

        grid = self.grid
        data = self.get_polygon_sample()

        fig, ax = plt.subplots()
        grid.plot(ax=ax, color=self.GRIDPOINTS_COLOR, markersize=1)
        data.plot(ax=ax, color=self.DATAPOINTS_COLOR, markersize=5)
        plt.xticks(rotation=90)
        return ax

