
import os
from .read.readmdb import ReadMdb
from .read.readshape import ReadPolyShape 

class MapTables:
    """
    A MapTables object gives access to the administrative data of a vegetation
    map, the What behind the Where of a polygon on a map.
    """

    def __init__(self,shape=None,mdb=None):

        #    if not isinstance(shape.shapegeopandas.geodataframe.GeoDataFrame
        self._shape = shape
        self._mdb = mdb

    @classmethod
    def from_files(cls,mdbpath,shppath):
        """
        Create MapTables object from files 

        Parameters
        ----------
        mdbpath : str
            Valid filepath to MS Access mdbfile
        shppath : str
            Valid filepath to ESRI shapefile

        Returns
        -------
        DsReader.Maptables
        """

        try:
            mdb = ReadMdb(mdbpath)
            shp = ReadPolyShape(shppath,fix_errors=True)
        except:
            pass

        return cls(shape=shp,mdb=mdb)


    def get_map(self):
        """  """ 
        self._mdb.table('Element')[['elmid','datum','locatietype','samengesteldelegenda','vereenvoudigdelegenda',
                'toevoeginglegenda','interpretatielegenda','abiotieklegenda','oppervlakte','sbbtype']]






