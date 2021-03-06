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
from .read.readshape import ReadPolyShape
from .read.readmdb import ReadMdb
from .filedirtools.listprojects import ListProjects

