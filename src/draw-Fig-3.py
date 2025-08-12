import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.colors as mcolors
from matplotlib import pyplot as plt
from matplotlib.colors import BoundaryNorm
import os

China_provinces = gpd.read_file('../data/China-maps/province.shp')
China_boundary = gpd.read_file('../data/China-maps/boundary.shp')
China_counties = gpd.read_file('../data/China-maps/county.shp')
China_provinces2 = gpd.read_file('../data/China-maps-simplified/province.shp')
China_counties2 = gpd.read_file('../data/China-maps-simplified/county.shp')
China_provinces['geometry'] = China_provinces2['geometry']
China_counties['geometry'] = China_counties2['geometry']
China_counties = China_counties.drop([176, 2403])

future_county_cement_POP = pd.read_csv(os.path.join('..', 'outputs', f'China_county_cement_POP_SSP2.csv'))
future_county_cement_GDP = pd.read_csv(os.path.join('..', 'outputs', f'China_county_cement_GDP_SSP2.csv'))
future_county_cement_combined = pd.read_csv(os.path.join('..', 'outputs', f'China_county_cement_combined_SSP2.csv'))

# future_county_cement_POP.columns = China_counties.index.tolist()
# future_county_cement_GDP.columns = China_counties.index.tolist()
# future_county_cement_combined.columns = China_counties.index.tolist()

future_county_cement_POP = future_county_cement_POP.drop([638, 639], axis=0)
future_county_cement_GDP = future_county_cement_GDP.drop([638, 639], axis=0)
future_county_cement_combined = future_county_cement_combined.drop([638, 639], axis=0) 

China_counties = China_counties.drop([638, 639])

China_provinces = China_provinces.to_crs(2381)
China_boundary = China_boundary.to_crs(2381)
China_counties = China_counties.to_crs(2381)


for t in range(2020, 2055, 5):
    China_counties[f'cement_{t}_POP'] = future_county_cement_POP.loc[:, str(t)].values
    China_counties[f'cement_{t}_GDP'] = future_county_cement_GDP.loc[:, str(t)].values
    China_counties[f'cement_{t}_combined'] = future_county_cement_combined.loc[:, str(t)].values

    China_counties[f'difference_{t}_GDP'] = China_counties[f'cement_{t}_GDP'] - China_counties[f'cement_{t}_POP']
    China_counties[f'difference_{t}_combined'] = China_counties[f'cement_{t}_combined'] - China_counties[f'cement_{t}_POP']


fig = plt.figure(figsize=(9, 7.5), constrained_layout=True)

years = [2030, 2030, 2030, 2040, 2040, 2040, 2050, 2050, 2050]
scenarios = ['POP', 'GDP', 'combined', 'POP', 'GDP', 'combined', 'POP', 'GDP', 'combined']

for i in range(1, 10):
    axx = plt.subplot(3, 3, i)
    China_provinces.plot(color='none', edgecolor='lightgrey' if i in [1, 4, 7] else 'k', lw=0.3, zorder=7, ax=axx)
    China_provinces[China_provinces['省'] == '台湾省'].plot(color='none', edgecolor='k', lw=0.3, zorder=10, ax=axx)
    China_counties.plot(color='lightgrey', edgecolor='w', lw=0.1, zorder=1, ax=axx)
    axx.set(ylim=(1.9*10**6, 6.3*10**6), xticks=[], yticks=[])
    # axx.axis('off')

    cax2 = axx.inset_axes([0.87, 0.015, 0.12, 0.20])
    China_provinces.plot(color='none', lw=0.2, ax=cax2)
    China_boundary.plot(color='k', edgecolor='k', lw=1.0, ax=cax2)
    cax2.spines[:].set_linewidth(.5)
    cax2.set(xlim=(0.3*10**6, 2.0*10**6), ylim=(0.3*10**6, 2.65*10**6), xticks=[], yticks=[])

    if i == 1:
        axx.set(title='POP')
     
    if i == 2: 
        axx.set(title='GDP')
    
    if i == 3:
        axx.set(title='POP-GDP')

    
    if i in [1, 4, 7]:
        cmap_1 = 'magma'
        bounds_1 = [0, 200, 400, 600, 800, 1e3, 2e3, 10e3]
        norm_1 = mcolors.BoundaryNorm(bounds_1, plt.cm.Blues.N) 
        China_counties.plot(column=f'cement_{years[i-1]}_{scenarios[i-1]}', norm=norm_1, cmap=cmap_1, zorder=6, lw=0.1, edgecolor='grey', ax=axx)

    else:
        # cmap_2 = 'BrBG_r'
        cmap_2 = 'RdYlBu_r'
        # bounds_2 = [-2e3, -1e3, -5e2, -1e2, 0, 1e2, 5e2, 1e3, 2e3]
        bounds_2 = [-8e3, -1e3, -5e2, -1e2, 0, 1e2, 5e2, 1e3, 8e3]
        norm_2 = mcolors.BoundaryNorm(bounds_2, plt.cm.Blues.N)
        China_counties.plot(column=f'difference_{years[i-1]}_{scenarios[i-1]}', norm=norm_2, cmap=cmap_2, zorder=6, lw=0.1, edgecolor='grey', ax=axx)


    if i == 7:
        cax1 = axx.inset_axes([0.10, -0.1, 0.80, 0.05]) 
        # Add a custom colorbar
        sm = plt.cm.ScalarMappable(cmap=cmap_1, norm=norm_1)
        sm.set_array([])
        cbar = plt.colorbar(sm, cax=cax1, orientation='horizontal', label='demand (Mt cement/year)')
        cbar.ax.set_xticklabels([0, 0.2, 0.4, 0.6, 0.8, 1, 2, 12])

        cbar.ax.tick_params(labelsize=9, rotation=0)
    
    elif i in [8, 9]:
        cax1 = axx.inset_axes([0.10, -0.1, 0.80, 0.05]) 
        # Add a custom colorbar
        sm = plt.cm.ScalarMappable(cmap=cmap_2, norm=norm_2)
        sm.set_array([])
        cbar = plt.colorbar(sm, cax=cax1, orientation='horizontal', label='∆ demand (Mt cement/year)')
        cbar.ax.set_xticklabels([-8, -1, -0.5, -0.1, 0, 0.1, 0.5, 1, 8])
        cbar.ax.tick_params(labelsize=9, rotation=0)


fig.text(0.025, 0.94, 'a', fontsize=14, fontdict={'weight': 'semibold'})
fig.text(0.36, 0.94, 'b', fontsize=14, fontdict={'weight': 'semibold'})
fig.text(0.69, 0.94, 'c', fontsize=14, fontdict={'weight': 'semibold'})
fig.text(0.025, 0.64, 'd', fontsize=14, fontdict={'weight': 'semibold'})
fig.text(0.36, 0.64, 'e', fontsize=14, fontdict={'weight': 'semibold'})
fig.text(0.69, 0.64, 'f', fontsize=14, fontdict={'weight': 'semibold'})
fig.text(0.025, 0.35, 'g', fontsize=14, fontdict={'weight': 'semibold'})
fig.text(0.36, 0.35, 'h', fontsize=14, fontdict={'weight': 'semibold'})
fig.text(0.69, 0.35, 'i', fontsize=14, fontdict={'weight': 'semibold'})


fig.text(0.025, 0.69, '2030', fontsize=12, fontdict={'weight': 'semibold'})
fig.text(0.36, 0.69, '2030', fontsize=12, fontdict={'weight': 'semibold'})
fig.text(0.69, 0.69, '2030', fontsize=12, fontdict={'weight': 'semibold'})
fig.text(0.025, 0.39, '2040', fontsize=12, fontdict={'weight': 'semibold'})
fig.text(0.36, 0.39, '2040', fontsize=12, fontdict={'weight': 'semibold'})
fig.text(0.69, 0.39, '2040', fontsize=12, fontdict={'weight': 'semibold'})
fig.text(0.025, 0.10, '2050', fontsize=12, fontdict={'weight': 'semibold'})
fig.text(0.36, 0.10, '2050', fontsize=12, fontdict={'weight': 'semibold'})
fig.text(0.69, 0.10, '2050', fontsize=12, fontdict={'weight': 'semibold'})

plt.show()
fig.savefig('../figures/Fig_3.jpg', dpi=600, bbox_inches='tight')