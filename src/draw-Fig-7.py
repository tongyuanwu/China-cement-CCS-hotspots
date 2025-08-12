import numpy as np
import pandas as pd
import geopandas as gpd
from matplotlib import pyplot as plt
import matplotlib.colors as mcolors
import seaborn as sns
import os

China_provinces = gpd.read_file('../data/China-maps/province.shp')
China_boundary = gpd.read_file('../data/China-maps/boundary.shp')
China_counties = gpd.read_file('../data/China-maps/county.shp')
China_provinces2 = gpd.read_file('../data/China-maps-simplified/province.shp')
China_counties2 = gpd.read_file('../data/China-maps-simplified/county.shp')
China_provinces['geometry'] = China_provinces2['geometry']
China_counties['geometry'] = China_counties2['geometry']
China_counties = China_counties.drop([176, 638, 639, 2403])
China_counties = China_counties.reset_index(drop=True)

China_provinces = China_provinces.to_crs(2381)
China_boundary = China_boundary.to_crs(2381)
China_counties = China_counties.to_crs(2381)

county_CO2_POP = pd.read_csv('../outputs/China_county_CO2_POP.csv', index_col=0)
county_CO2_GDP = pd.read_csv('../outputs/China_county_CO2_GDP.csv', index_col=0)
county_CO2_combined = pd.read_csv('../outputs/China_county_CO2_combined.csv', index_col=0)


cum_CO2_2050_POP = pd.Series((county_CO2_POP.loc[2021:2050].sum() / 1e3).values.round(1).tolist())
cum_CO2_2050_GDP = pd.Series((county_CO2_GDP.loc[2021:2050].sum() / 1e3).values.round(1).tolist())
cum_CO2_2050_combined = pd.Series((county_CO2_combined.loc[2021:2050].sum() / 1e3).values.round(1).tolist())


China_counties['cum_CO2_2050_POP'] = np.where(cum_CO2_2050_POP.values == 0, np.nan, cum_CO2_2050_POP.values)
China_counties['cum_CO2_2050_GDP'] = np.where(cum_CO2_2050_GDP.values == 0, np.nan, cum_CO2_2050_GDP.values) 
China_counties['cum_CO2_2050_combined'] = np.where(cum_CO2_2050_combined.values == 0, np.nan, cum_CO2_2050_combined.values)

China_counties['diff_CO2_2050_GDP'] = (China_counties['cum_CO2_2050_GDP'].fillna(0) - China_counties['cum_CO2_2050_POP'].fillna(0)).where(China_counties['cum_CO2_2050_GDP'].notnull() | China_counties['cum_CO2_2050_POP'].notnull())
China_counties['diff_CO2_2050_combined'] = (China_counties['cum_CO2_2050_combined'].fillna(0) - China_counties['cum_CO2_2050_POP'].fillna(0)).where(China_counties['cum_CO2_2050_combined'].notnull() | China_counties['cum_CO2_2050_POP'].notnull())

China_counties['diff_CO2_2050_GDP'] = China_counties['diff_CO2_2050_GDP'].replace(0, np.nan)
China_counties['diff_CO2_2050_combined'] = China_counties['diff_CO2_2050_combined'].replace(0, np.nan)


fig = plt.figure(figsize=(9, 4), constrained_layout=True)

ax1 = plt.subplot(1, 3, 1)
bounds_E = [0, 5, 10, 20, 50, 100, 200, 300]
norm_E = mcolors.BoundaryNorm(bounds_E, plt.cm.Blues.N) 
cmap_1 = 'RdPu'
China_provinces.plot(color='none', lw=0.20, zorder=6, ax=ax1)
China_counties.plot(
    column='cum_CO2_2050_POP', 
    norm=norm_E, 
    cmap=cmap_1, 
    edgecolor='lightgrey',
    lw=0.2,
    legend=False,
    zorder=5,
    ax=ax1)    
China_counties.plot(color='whitesmoke', edgecolor='lightgrey', lw=0.1, zorder=1, ax=ax1)
ax1.set(ylim=(1.9*10**6, 6.3*10**6), xticks=[], yticks=[], title='')
ax1.axis('off')

cax1 = ax1.inset_axes([0.2, -0.1, 0.6, 0.05]) 
# Add a custom colorbar
sm = plt.cm.ScalarMappable(cmap=cmap_1, norm=norm_E)
sm.set_array([])
cbar = plt.colorbar(sm, cax=cax1, orientation='horizontal', label='$CE$ (Mt-CO$_{2}$)')
cbar.ax.set_xticklabels(bounds_E)
cbar.ax.tick_params(labelsize=9, rotation=0)

cax1_2 = ax1.inset_axes([0.87, 0.015, 0.12, 0.20])
China_provinces.plot(color='none', lw=0.2, ax=cax1_2)
China_boundary.plot(color='k', edgecolor='k', lw=1.0, ax=cax1_2)
cax1_2.spines[:].set_linewidth(.5)
cax1_2.set(xlim=(0.3*10**6, 2.0*10**6), ylim=(0.3*10**6, 2.65*10**6), xticks=[], yticks=[])

for i, scenario in enumerate(['GDP', 'combined']): 
    ax2 = plt.subplot(1, 3, 2+i)
    bounds_changes = [-100, -50, -10, -5, 0, 5, 10, 50, 100]
    norm_changes = mcolors.BoundaryNorm(bounds_changes, plt.cm.Blues.N) 
    cmap_2 = 'RdBu_r'
    China_provinces.plot(color='none', lw=0.20, zorder=6, ax=ax2)
    China_counties.plot(
        column=f'diff_CO2_2050_{scenario}', 
        norm=norm_changes, 
        cmap=cmap_2, 
        edgecolor='lightgrey',
        lw=0.2,
        legend=False,
        zorder=5,
        ax=ax2)    
    China_counties.plot(color='whitesmoke', edgecolor='lightgrey', lw=0.1, zorder=1, ax=ax2)
    ax2.set(ylim=(1.9*10**6, 6.3*10**6), xticks=[], yticks=[], title='')
    ax2.axis('off')

    cax2 = ax2.inset_axes([0.15, -0.1, 0.7, 0.05]) 
    # Add a custom colorbar
    sm2 = plt.cm.ScalarMappable(cmap=cmap_2, norm=norm_changes)
    sm2.set_array([])
    cbar2 = plt.colorbar(sm2, cax=cax2, orientation='horizontal', label='change in $CE$ (Mt-CO$_{2}$)')
    cbar2.ax.set_xticklabels(bounds_changes)
    cbar2.ax.tick_params(labelsize=9, rotation=0)

    cax2_2 = ax2.inset_axes([0.87, 0.015, 0.12, 0.20])
    China_provinces.plot(color='none', lw=0.2, ax=cax2_2)
    China_boundary.plot(color='k', edgecolor='k', lw=1.0, ax=cax2_2)
    cax2_2.spines[:].set_linewidth(.5)
    cax2_2.set(xlim=(0.3*10**6, 2.0*10**6), ylim=(0.3*10**6, 2.65*10**6), xticks=[], yticks=[])


fig.text(0.00, 0.76, 'a', fontsize=14, fontdict={'weight': 'semibold'})
fig.text(0.35, 0.76, 'b', fontsize=14, fontdict={'weight': 'semibold'})
fig.text(0.68, 0.76, 'c', fontsize=14, fontdict={'weight': 'semibold'})

plt.show()
fig.savefig('../figures/Fig_7.jpg', dpi=600, bbox_inches='tight')