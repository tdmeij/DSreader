"""
DSreader is a python package for reading data from vegetation maps 
organised according to the Digital Standard.

The digital Standard is a dataformat developed in the nineties
by the Dutch National Forestry Service (Staatsbosbeheer). A vegetion
map comprises an ESRI shapefile with polygons and an Microsoft Access 
database with information about the content of the polygons.

Classes
-------
ListProjects
    Create table of filenames organised by project under a given root file
ReadMdb
    Read Microsoft Access .mdb file and extract tables as pd.DataFrame
ReadPolyShape
    Read ESRI Shapefile with vegetation polygons

"""

# import classes
from .maptables import MapTables
from .mapelements import MapElements
from .mapdata import MapData
from .read.readshapefile import ReadShapeFile
from .read.readmdb import ReadMdb
from .tools.listprojects import ListProjects
from .data import data

# import functions
from .tools.filetools import relativepaths as relativepaths
from .tools.filetools import absolutepaths as absolutepaths
