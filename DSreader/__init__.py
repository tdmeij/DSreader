"""
DSreader is a python package for reading data from vegetation maps 
organised according to the Digital Standard.

The digital Standard is a dataformat developed in the nineties
by the Dutch National Forestry Service (Staatsbosbeheer). A vegetion
map comprises an ESRI shapefile with polygons and an Microsoft Access 
database with information about the content of the polygons.

Main package classes
--------------------
MapData
    Manage vegetion map data and connect spatial data to non-spatial
    data.

Helper classes
--------------
ListProjects
    Create table of filenames organised by project under a given root file
MapElements
    Manage spatial data for map elements.
MapTables
    Manage tables with non-spatial data related to mapped elements.
ReadMdb
    Read Microsoft Access .mdb file and extract tables as pd.DataFrame.
ReadShapeFile
    Read ESRI Shapefile and correct errors if necessary.

Classes for spatial analysis
----------------------------
SamplePolygonMap
    Create regular grid and sample polygon map at grid points.
SankeyTwoMaps
    Plot Sankey flow chart comparing changes in management quality between 
    two maps.
   
"""

# import classes
from .maptables import MapTables
from .mapelements import MapElements
from .mapdata import MapData
from .read.readshapefile import ReadShapeFile
from .read.readmdb import ReadMdb
from .sample.samplepolygonmap import SamplePolygonMap
from .tools.projectstable import ProjectsTable
from .plot.sankey_two_maps import SankeyTwoMaps
from .tools.conversions import year_from_string
from .tools.write_excel import write_to_excel
from .data import data

# import functions
from .tools.filetools import relativepath as relativepath
from .tools.filetools import absolutepath as absolutepath
