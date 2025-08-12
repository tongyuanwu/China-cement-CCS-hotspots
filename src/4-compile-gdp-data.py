import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio as rio
from rasterio.windows import from_bounds
import os
from tqdm import tqdm

names = locals()
China_counties = gpd.read_file('../data/China-maps/county.shp')
global_GDP_raster_2020_ = rio.open('../data/GDP-2010-2020/GDP2020.tif')
China_county_raster_ = rio.open('../outputs/China_county_raster.tif')

China_county_raster = China_county_raster_.read(1)

for t in range(2025, 2055, 5):
    for i in range(1, 6):
        a_path = os.path.join('..', 'data', 'future-gdp-1km', f'SSP{i}', f'GDP{t}_ssp{i}.tif')
        names[f'global_GDP_raster_{t}_SSP{i}_'] = rio.open(a_path)

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
    transform=global_GDP_raster_2020_.transform 
)

China_GDP_raster_2020_SSP1 = global_GDP_raster_2020_.read(1, window=China_window)
China_GDP_raster_2020_SSP2 = global_GDP_raster_2020_.read(1, window=China_window)
China_GDP_raster_2020_SSP3 = global_GDP_raster_2020_.read(1, window=China_window)
China_GDP_raster_2020_SSP4 = global_GDP_raster_2020_.read(1, window=China_window)
China_GDP_raster_2020_SSP5 = global_GDP_raster_2020_.read(1, window=China_window)

for t in range(2025, 2055, 5):
    for i in range(1, 6):
        names[f'China_GDP_raster_{t}_SSP{i}'] = names[f'global_GDP_raster_{t}_SSP{i}_'].read(1, window=China_window)

# compile GDP data
for t in tqdm(range(2020, 2055, 5)):
    China_counties[f'GDP_{t}_SSP1'] = np.nan
    China_counties[f'GDP_{t}_SSP2'] = np.nan
    China_counties[f'GDP_{t}_SSP3'] = np.nan
    China_counties[f'GDP_{t}_SSP4'] = np.nan
    China_counties[f'GDP_{t}_SSP5'] = np.nan

    for i in China_counties.index:
        a_county_gdp_ssp1 = np.nansum(names[f'China_GDP_raster_{t}_SSP1'][China_county_raster == i+1]).round()
        a_county_gdp_ssp2 = np.nansum(names[f'China_GDP_raster_{t}_SSP2'][China_county_raster == i+1]).round()
        a_county_gdp_ssp3 = np.nansum(names[f'China_GDP_raster_{t}_SSP3'][China_county_raster == i+1]).round()
        a_county_gdp_ssp4 = np.nansum(names[f'China_GDP_raster_{t}_SSP4'][China_county_raster == i+1]).round()
        a_county_gdp_ssp5 = np.nansum(names[f'China_GDP_raster_{t}_SSP5'][China_county_raster == i+1]).round()

        China_counties.loc[i, f'GDP_{t}_SSP1'] = a_county_gdp_ssp1
        China_counties.loc[i, f'GDP_{t}_SSP2'] = a_county_gdp_ssp2
        China_counties.loc[i, f'GDP_{t}_SSP3'] = a_county_gdp_ssp3
        China_counties.loc[i, f'GDP_{t}_SSP4'] = a_county_gdp_ssp4
        China_counties.loc[i, f'GDP_{t}_SSP5'] = a_county_gdp_ssp5


China_counties[['省', '市', '县', '县代码'] + [f'GDP_{t}_SSP1' for t in range(2020, 2055, 5)]].to_csv('../outputs/China_county_GDP_SSP1.csv', index=False, encoding='utf-8-sig')
China_counties[['省', '市', '县', '县代码'] + [f'GDP_{t}_SSP2' for t in range(2020, 2055, 5)]].to_csv('../outputs/China_county_GDP_SSP2.csv', index=False, encoding='utf-8-sig')
China_counties[['省', '市', '县', '县代码'] + [f'GDP_{t}_SSP3' for t in range(2020, 2055, 5)]].to_csv('../outputs/China_county_GDP_SSP3.csv', index=False, encoding='utf-8-sig')
China_counties[['省', '市', '县', '县代码'] + [f'GDP_{t}_SSP4' for t in range(2020, 2055, 5)]].to_csv('../outputs/China_county_GDP_SSP4.csv', index=False, encoding='utf-8-sig')
China_counties[['省', '市', '县', '县代码'] + [f'GDP_{t}_SSP5' for t in range(2020, 2055, 5)]].to_csv('../outputs/China_county_GDP_SSP5.csv', index=False, encoding='utf-8-sig')