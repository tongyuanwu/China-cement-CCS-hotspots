import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio as rio
from rasterio.features import rasterize
from rasterio.windows import from_bounds

China_counties = gpd.read_file('../data/China-maps/county.shp')
global_population_raster = rio.open('../data/future-pop-1km/SSP2/SSP2_2030.tif')

county_shape_ids = [(geom, value+1) for geom, value in zip(China_counties.geometry, China_counties.index.values)]

China_bbox = {
    "min_lon": 73.5,  # Westernmost longitude
    "min_lat": 18.1,  # Southernmost latitude
    "max_lon": 135.0, # Easternmost longitude
    "max_lat": 53.6   # Northernmost latitude
}

China_window = from_bounds(
    left=China_bbox['min_lon'], 
    bottom=China_bbox['min_lat'],
    right=China_bbox['max_lon'], 
    top=China_bbox['max_lat'], 
    transform=global_population_raster.transform
)

China_raster_transform = global_population_raster.window_transform(China_window)
print(China_raster_transform)

China_population_raster = global_population_raster.read(1, window=China_window) 

China_county_raster = rasterize(
    shapes=county_shape_ids, 
    out_shape=China_population_raster.shape, 
    transform=China_raster_transform, 
    fill=0,    # Value for areas outside counties
    dtype='int32',
)


with rio.open(
    '../outputs/China_county_raster.tif', 
    "w", 
    driver="GTiff", 
    height=China_county_raster.shape[0], 
    width=China_county_raster.shape[1], 
    count=1, 
    dtype=China_county_raster.dtype, 
    crs=global_population_raster.crs, 
    transform=China_raster_transform,
    compress='lzw',
    ) as dst: 
    dst.write(China_county_raster, 1)
