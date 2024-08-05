
import pytest
from geopandas import GeoSeries, GeoDataFrame
import geopandas as gpd

import matplotlib

from DSreader import SamplePolygonMap

@pytest.fixture
def root():
    return r'.\data\DSprojects\\'

@pytest.fixture
def polyshape(root):
    fpath=root+'Drenthe\\Dr 0007_Hijken_1989\\vlakken.shp'
    return gpd.read_file(fpath)


# test class mathods
# ------------------

def test_gridbounds(polyshape):
    bbox = SamplePolygonMap.create_gridbounds(polyshape)
    assert isinstance(bbox, dict)
    assert all([key in bbox.keys() for key in ['xmin','xmax','ymin','ymax']])

def test_regulargrid():
    gdf = SamplePolygonMap.create_regular_grid(
        step=100.,
        xmin=204500.,
        xmax=205000.,
        ymin=499500.,
        ymax=500000.,
        )
    assert isinstance(gdf, GeoDataFrame)
    assert not gdf.empty

def test_sampling_grid(polyshape):

    # regular grid
    gdf = SamplePolygonMap.create_sampling_grid(
        polyshape, gridtype='regular', step=100.,)
    assert isinstance(gdf, GeoDataFrame)
    assert not gdf.empty

    # representative point
    gdf = SamplePolygonMap.create_sampling_grid(
        polyshape, gridtype='repr')
    assert isinstance(gdf, GeoSeries)
    assert not gdf.empty


# test init
# ---------

def test_init_without_shape():
    with pytest.raises(TypeError):
        SamplePolygonMap()

def test_init_with_defaults(polyshape):
    smp = SamplePolygonMap(polyshape)
    assert isinstance(smp, SamplePolygonMap)

def test_init_regular_grid(polyshape):
    smp = SamplePolygonMap(polyshape, gridtype='regular', step=100,
        crs='epsg:28992')
    assert isinstance(smp, SamplePolygonMap)

def test_init_representative_points(polyshape):
    smp = SamplePolygonMap(polyshape, gridtype='repr',
        crs='epsg:28992')
    assert isinstance(smp, SamplePolygonMap)

# test methods
# ------------

def test_get_polygon_sample(polyshape):
    smp = SamplePolygonMap(polyshape)
    gdf = smp.get_polygon_sample()
    assert isinstance(gdf, GeoDataFrame)
    assert not gdf.empty

# test properties
# ---------------

def test_repr(polyshape):
    smp = SamplePolygonMap(polyshape)
    assert isinstance(str(smp), str)

def test_grid(polyshape):
    smp = SamplePolygonMap(polyshape)
    grid = smp.grid
    assert isinstance(grid, gpd.GeoDataFrame)

def test_polygons(polyshape):
    smp = SamplePolygonMap(polyshape)
    polys = smp.polygons
    assert isinstance(polys, gpd.GeoDataFrame)

