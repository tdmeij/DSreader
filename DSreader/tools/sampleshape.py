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

    def __init__(self,polygons):
        """
        Parameters
        ----------
        polygons : geopandas.GeoDataFrame
            Polygon map.
        """

        if not isinstance(polygons,gpd.geodataframe.GeoDataFrame):
            raise Exception(f'Expect class GeoDataFrame, not {shape.__class__}')
        self._poly = polygons


    def __repr__(self):
        npoly = len(self._poly)
        return f'{self.__class__.__name__} ({npoly} polygons)'       
        ##return (f'{self._poly}')

    def gridbounds(self,step=100):
        """Return four boundary points for a sample grid that covers entire 
        polygon shape
        
        Parmeters
        ---------
        step : number, default 100
            Distance between sample points.
        
        Returns
        -------
        xlim,ylim
        """
        bnd = self._poly.total_bounds
        xmin = bnd[0] - (bnd[0] % step)
        xmax = bnd[2] - (bnd[2] % step) + step
        ymin = bnd[1] - (bnd[1] % step)
        ymax = bnd[3] - (bnd[3] % step) + step
        return [xmin,xmax],[ymin,ymax]


    def gridpoints(self,step=100,xlim=None,ylim=None,crs='epsg:28992'):
        """Return geodataframe with points in regular grid
        
        Parameters
        ----------
        step : number, default 100
            Regular grid points interval.
        xlim : list or tuple, optional
            Horizontal grid limits as (xmin,ymin)
        ylim : list or tuple, optional
            Vertical grid limts as (ymin,ymax)
        crs : map crs, default 'epsg:28992'
        
        Returns
        -------
        geopandas.GeoDataFrame
        
        """

        if (xlim is None) or (ylim is None):
            xlim,ylim = self.gridbounds(step=step)

        xp = np.arange(xlim[0],xlim[1],step)
        yp = np.arange(ylim[0],ylim[1],step)
        xx, yy = np.meshgrid(xp, yp)
        pointgeom = gpd.points_from_xy(xx.flatten(), yy.flatten(), crs=crs)
        gridpoints = gpd.GeoDataFrame(geometry=pointgeom)
        return gridpoints

    def sample(self,gridpoints=None,xlim=None,ylim=None,step=100):
        """
        Return gridpoints with polygon values
        
        Parameters
        ----------
        gridpoints : geopandas.GeoDataFrame, optional
            Existing grid points, sample values will be added to 
            attribute table. If not given, a new sample grid will 
            be created.
        xlim : list or tuple, optional
            Horizontal grid limits as (xmin,ymin)
        ylim : list or tuple, optional
            Vertical grid limts as (ymin,ymax)       
        step : number, default 100
            Regular grid points interval.

        """

        if gridpoints is not None:
            if not isinstance(gridpoints,gpd.geodataframe.GeoDataFrame):
                raise Exception(f'Expect class GeoDataFrame, not {gridpoints.__class__}')
            self._gridpoints = gridpoints

        if (gridpoints is None) & (xlim is not None) & (ylim is not None):
            crs = 'epsg:28992'
            self._gridpoints = self.gridpoints(xlim=xlim,ylim=ylim,step=step,crs=crs)

        if gridpoints is None:
            self._gridpoints = self.gridpoints(step=step)

        sample = gpd.sjoin(self._gridpoints,self._poly,how='inner',op='within')
        if 'index_right' in sample.columns:
            sample = sample.drop(columns=['index_right'])
        return sample
