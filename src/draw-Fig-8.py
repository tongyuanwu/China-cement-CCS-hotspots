import numpy as np
import pandas as pd
import geopandas as gpd
from matplotlib import pyplot as plt
import matplotlib.colors as mcolors
import matplotlib as mpl
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

storage_capacity = pd.read_csv('../outputs/China_county_carbon_storage.csv', )
storage_capacity = storage_capacity.drop([176, 638, 639, 2403])
storage_capacity = storage_capacity.reset_index(drop=True)

China_counties['G_DSA'] = storage_capacity['G_DSA']
China_counties['G_EOR'] = storage_capacity['G_EOR']


fig = plt.figure(figsize=(9, 3.5), constrained_layout=True)

ax1 = plt.subplot(1, 2, 1)
cax1 = ax1.inset_axes((0.05, 0.10, 0.25, 0.02))
China_provinces.plot(color='none', lw=0.20, zorder=5, ax=ax1)
China_counties.plot(
    column='G_DSA', 
    norm=mpl.colors.LogNorm(1, 3000), 
    cmap='Blues', 
    edgecolor='lightgrey',
    lw=0.2,
    legend=True,
    legend_kwds={'orientation': 'horizontal', 'cax': cax1, 'label': 'G$_{DSA}$ (Mt-CO$_{2}$)'}, 
    ax=ax1)
China_provinces[China_provinces['省'] == '台湾省'].plot(color='lightgrey', zorder=10, ax=ax1)
ax1.set(ylim=(1.9*10**6, 6.3*10**6), xticks=[], yticks=[], title='')
# ax1.text(-2.2*10**6, 2.5*10**6, 'Mt CO$_{2}$', fontsize=9)
ax1.axis('off')
cax1.tick_params(labelsize='small')
cax1.set_xticks([1, 10, 100, 3000], labels=[1, 10, 100, 3000])

cax1_3 = ax1.inset_axes([0.05, 0.12, 0.25, 0.20])
sns.histplot(China_counties['G_DSA'].values, bins=np.logspace(1, 3.478, 50), color='steelblue', alpha=0.5, ax=cax1_3)
cax1_3.set(xlim=(10, 3000), xscale='log')
cax1_3.axis('off')

cax1_2 = ax1.inset_axes([0.87, 0.01, 0.12, 0.20])
China_provinces.plot(color='none', lw=0.2, ax=cax1_2)
China_boundary.plot(color='k', edgecolor='k', lw=1.0, ax=cax1_2)
cax1_2.spines[:].set_linewidth(.5)
cax1_2.set(xlim=(0.3*10**6, 2.0*10**6), ylim=(0.3*10**6, 2.65*10**6), xticks=[], yticks=[])


ax2 = plt.subplot(1, 2, 2)
cax2 = ax2.inset_axes((0.05, 0.10, 0.25, 0.02))
China_provinces.plot(color='none', lw=0.20, zorder=5, ax=ax2)
China_counties.plot(
    column='G_EOR', 
    norm=mpl.colors.LogNorm(1, 3000), 
    cmap='Reds', 
    edgecolor='lightgrey',
    lw=0.2,
    legend=True,
    legend_kwds={'orientation': 'horizontal', 'cax': cax2, 'label': 'G$_{EOR}$ (Mt-CO$_{2}$)'}, 
    ax=ax2)
China_provinces[China_provinces['省'] == '台湾省'].plot(color='lightgrey', zorder=10, ax=ax2)
ax2.set(ylim=(1.9*10**6, 6.3*10**6), xticks=[], yticks=[], title='')
# ax2.text(-2.2*10**6, 2.5*10**6, 'Mt CO$_{2}$', fontsize=9)
ax2.axis('off')
cax2.tick_params(labelsize='small')
cax2.set_xticks([1, 10, 100, 3000], labels=[1, 10, 100, 3000])

cax2_3 = ax2.inset_axes([0.05, 0.12, 0.25, 0.20])
sns.histplot(China_counties['G_EOR'].values, bins=np.logspace(1, 3.478, 50), color='r', alpha=0.5, ax=cax2_3)
cax2_3.set(xlim=(10, 3000), xscale='log')
cax2_3.axis('off')


cax2_2 = ax2.inset_axes([0.87, 0.01, 0.12, 0.20])
China_provinces.plot(color='none', lw=0.2, ax=cax2_2)
China_boundary.plot(color='k', edgecolor='k', lw=1.0, ax=cax2_2)
cax2_2.spines[:].set_linewidth(.5)
cax2_2.set(xlim=(0.3*10**6, 2.0*10**6), ylim=(0.3*10**6, 2.65*10**6), xticks=[], yticks=[])


fig.text(0.01, 0.93, 'a', fontsize=14, fontdict={'weight': 'semibold'})
fig.text(0.51, 0.93, 'b', fontsize=14, fontdict={'weight': 'semibold'})

plt.show()
fig.savefig('../figures/Fig_8.jpg', dpi=600, bbox_inches='tight')