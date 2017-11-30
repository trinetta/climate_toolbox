#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `climate_toolbox` package."""

import pytest

from click.testing import CliRunner

from climate_toolbox import climate_toolbox as ctb
from climate_toolbox import cli

import numpy as np
import pandas as pd
import pytest
import xarray as xr
import itertools


#python utils

#create pytest resource to be used across tests

@pytest.fixture(scope='session')
def lat():

    return np.arange(-89.875, 90, 2)


@pytest.fixture(scope='session')
def lon():

    return np.arange(0.125, 360.0, 2)


@pytest.fixture(scope='session')
def time():
    
    return pd.date_range(start=pd.datetime(2000, 1, 1), periods=10, freq='D')


@pytest.fixture
def clim_data(lat, lon, time):
    '''
    Generate fake climate data to do tests on
    '''
    np.random.seed(42)
    temp = np.random.rand(len(lat), len(lon), len(time))*100

    ds = xr.Dataset({'temperature': (['lat', 'lon', 'time'],  temp)}, 
                    coords={'lon':  lon,
                            'lat':  lat,
                            'time':time})

    return ds


def test_clim_data(clim_data):

    assert clim_data.isnull().any() == False


@pytest.fixture
def make_holes(clim_data, lat):

    N = len(lat) - 1

    tmp = clim_data['temperature'].values
    array = np.random.randint(0, N, 1)
    tmp[array] = np.nan

    clim_data['temperature'].values = tmp

    return clim_data


#create pytest resource to be used acress tessts
def test_fill_holes(make_holes):

    assert make_holes.isnull().any() == True
    ctb._fill_holes_xr(make_holes, 'temperature')

    assert make_holes.isnull().any() == False

@pytest.fixture
def weights(lat, lon):
    '''
    Create a weights fixture used for weighted computations
    '''

    df = pd.DataFrame()
    lats = np.random.choice(lat, 100)
    lons = np.random.choice(lon, 100)
    df['lat'] = lats
    df['lon'] = lons
    
    df['areawt'] = np.random.random(len(df['lon']))
    tmp = np.random.random(len(df['lon']))
    tmp[::5] = np.nan
    df['popwt'] = tmp
    df['hierid'] = np.random.choice(np.arange(1,25), len(lats))
    mapping = {h: np.random.choice(np.arange(1,5)) for h in df['hierid'].values}
    df['ISO'] = [mapping[i] for i in df['hierid']]
    df.index.names = ['reshape_index']

    return df


def test_reindex_spatial_weights(clim_data, weights):

    assert clim_data.isnull().any() == False

    ds = ctb._reindex_spatial_data_to_regions(clim_data, weights)

    assert ds.temperature.shape == (len(ds['lon']), len(ds['time']))
    assert 'reshape_index' in ds.dims




def test_weighting(clim_data, weights):

    assert np.isnan(weights['popwt'].values).any() == True
    ds = ctb._reindex_spatial_data_to_regions(clim_data, weights)
    assert ds.temperature.isnull().any() == False

    wtd = ctb._aggregate_reindexed_data_to_regions(ds, 'temperature', 'popwt', 'ISO', weights)
    assert wtd.temperature.isnull().any() == False

    wtd = ctb._aggregate_reindexed_data_to_regions(ds, 'temperature', 'areawt', 'ISO', weights)
    assert wtd.temperature.isnull().any() == False


@pytest.fixture(scope='session')
def grid():
    '''
    Mock a gridded geospatial object
    Construct a box with smaller sub units that can be intersected with 
    a polygon to identify boundary and interior points
    '''
    #construct squares

    pass

@pytest.fixture(scope='session')
def polygons(grid):
    '''
    Use the grid definition to construct a set of arbitrary shaped polygons
    where the grid points are boundary and interior to the polygons 

    '''
    #construct triangles and other points
    pass

@pytest.fixture(scope='session')
def raster():
    '''
    Construct a synthetic raster of for each grid cell.
    Each cell should have a `count` and `mean` entry in a dictionary like object

    '''
    #make up raster data
    pass

@pytest.fixture(scope='session')
def intersected(grid, polygons):
    '''

    '''

    intersected = ctb._intersect_grid_admin(grid, polygons)



def test_grid_polygon_intersection(grid, polygons):
    '''
    Not sure what this would test, in some sort of set-theoretic way

    We want to test that every entry has some area. If a segment has no area
    It should not be included as a segment. 
    
    '''
    #intersected = ctb._intersect_grid_admin(grid, polygons)

    #something like this
    #assert not intersected.geometry.area.isnull().any()
    pass

def test_generate_weights(intersected, polygons, raster):
    '''
    Test to make sure that our weighting operations are properly
    allocating the pixel based weights to each grid cell and then
    doing the appropriate ratio allocation for each admin unit
    
    '''

    #weights = ctb._generate_weights(intersected, raster)

    #this tests to make sure our area adds to 1 for each admin unit of interest
    #assert weights['area_total'].all() == 1

    #this tests to make sure that our socio var of interests add to 1 for each 
    #unit admin unit of interest
    #assert weights['socio_total'].all() == 1

    #this tests whether or not we have values for each of our admin polygons
    #assert weights.groupby('unit_id').sum() == len(polygons)
    pass




# @pytest.fixture
# def response():
#     """Sample pytest fixture.

#     See more at: http://doc.pytest.org/en/latest/fixture.html
#     """
#     # import requests
#     # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')


# def test_content(response):
#     """Sample pytest test function with the pytest fixture as an argument."""
#     # from bs4 import BeautifulSoup
#     # assert 'GitHub' in BeautifulSoup(response.content).title.string


# def test_command_line_interface():
#     """Test the CLI."""
#     runner = CliRunner()
#     result = runner.invoke(cli.main)
#     assert result.exit_code == 0
#     assert 'climate_toolbox.cli.main' in result.output
#     help_result = runner.invoke(cli.main, ['--help'])
#     assert help_result.exit_code == 0
#     assert '--help  Show this message and exit.' in help_result.output



