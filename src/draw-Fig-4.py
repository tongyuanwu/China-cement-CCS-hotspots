import numpy as np
import pandas as pd
import geopandas as gpd
import gurobipy as gp
from gurobipy import GRB
from sklearn.cluster import DBSCAN, KMeans
from sklearn.metrics import r2_score, root_mean_squared_error
import math, time
from tqdm import tqdm
from matplotlib import pyplot as plt
import matplotlib.colors as mcolors
import seaborn as sns
import matplotlib as mpl
from matplotlib.patches import Circle
from matplotlib.patches import FancyArrowPatch
from matplotlib.colors import rgb2hex
from PIL import ImageColor
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.colors import BoundaryNorm


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

future_county_production_POP = pd.read_csv(r'../outputs/China_county_production_POP.csv', )
future_county_production_GDP = pd.read_csv(r'../outputs/China_county_production_GDP.csv', )
future_county_production_combined = pd.read_csv(r'../outputs/China_county_production_combined.csv', )

future_county_capacity_POP = pd.read_csv(r'../outputs/China_county_capacity_POP.csv', )
future_county_capacity_GDP = pd.read_csv(r'../outputs/China_county_capacity_GDP.csv', )
future_county_capacity_combined = pd.read_csv(r'../outputs/China_county_capacity_combined.csv', )

China_counties['production_2020_POP'] = future_county_production_POP['production_2020_POP'] / 1e3
China_counties['production_2020_GDP'] = future_county_production_GDP['production_2020_GDP'] / 1e3
China_counties['production_2020_combined'] = future_county_production_combined['production_2020_combined'] / 1e3

China_counties['capacities_2020_POP'] = future_county_capacity_POP['capacities_2020_POP'] / 1e3
China_counties['capacities_2020_GDP'] = future_county_capacity_GDP['capacities_2020_GDP'] / 1e3
China_counties['capacities_2020_combined'] = future_county_capacity_combined['capacities_2020_combined'] / 1e3

Wang_2023_clinker = pd.read_excel('../data/Wang_2023.xlsx', sheet_name='Clinker - production output')


t = 2020
aa = Wang_2023_clinker.groupby('所在市')['产量（万吨/年）'].sum() / 1e2
bb = China_counties.groupby('市')[f'production_{t}_POP'].sum() 
cc = China_counties.groupby('市')[f'production_{t}_GDP'].sum() 
dd = China_counties.groupby('市')[f'production_{t}_combined'].sum() 


estimated_values_POP = bb[aa.index.tolist()].values
estimated_values_GDP = cc[aa.index.tolist()].values
estimated_values_combined = dd[aa.index.tolist()].values
reference_values = aa.values

R2_POP = r2_score(reference_values, estimated_values_POP)
R2_GDP = r2_score(reference_values, estimated_values_GDP)
R2_combined = r2_score(reference_values, estimated_values_combined)
RMSE_POP = root_mean_squared_error(reference_values, estimated_values_POP)
RMSE_GDP = root_mean_squared_error(reference_values, estimated_values_GDP)
RMSE_combined = root_mean_squared_error(reference_values, estimated_values_combined)

# Define custom intervals for the color bar
bounds = [0, 2, 4, 6, 8, 10, 15, 27]  # Define the intervals
cmap = plt.cm.Blues
norm_1 = mcolors.BoundaryNorm(bounds, cmap.N) 

gg = plt.hist(China_counties[China_counties['capacities_2020_POP'] > 0]['capacities_2020_POP'].values, bins=[0, 2, 4, 6, 8, 10, 15, 26.1])
value_counts = gg[0]


fig = plt.figure(figsize=(10, 8), constrained_layout=True)

ax1 = plt.subplot(1, 1, 1)
cax1 = ax1.inset_axes([0.05, 0.13, 0.25, 0.03])
China_counties.plot(
    column='capacities_2020_POP', 
    cmap='Reds',
    norm=norm_1,
    lw=0.25,
    edgecolor='grey',
    zorder=5,
    legend=True,
    legend_kwds={'orientation':'horizontal', 'label': 'Mt per year'}, 
    cax=cax1,
    ax=ax1
)
China_counties.plot(color='lightgrey', edgecolor='w', lw=0.1, zorder=1, ax=ax1)
China_provinces.plot(color='none', edgecolor='k', lw=0.5, zorder=6, ax=ax1)
# ax1.set(xlim=(72, 136), ylim=(17, 55))
ax1.set(ylim=(1.9*10**6, 6.3*10**6))
ax1.axis('off')

cax2 = ax1.inset_axes([0.87, 0.015, 0.12, 0.20])
China_provinces.plot(color='none', lw=0.2, ax=cax2)
China_boundary.plot(color='k', edgecolor='k', lw=1.0, ax=cax2)
cax2.spines[:].set_linewidth(.5)
# cax2.set(xlim=(106, 124), ylim=(2, 22), xticks=[], yticks=[])
cax2.set(xlim=(0.3*10**6, 2.0*10**6), ylim=(0.3*10**6, 2.65*10**6), xticks=[], yticks=[]) 

cax3 = ax1.inset_axes([1.10, 0.55, 0.35, 0.35])
cax3.set(xlabel='capacity (Mt per year)', ylabel='production (Mt per year)', aspect=1.0, xlim=(0, 30), ylim=(0, 30))
cax3.scatter(China_counties[f'capacities_{t}_POP'], China_counties[f'production_{t}_POP'], s=40, alpha=.7, clip_on=False, zorder=5, label='POP')
cax3.scatter(China_counties[f'capacities_{t}_GDP'], China_counties[f'production_{t}_GDP'], s=40, alpha=.7, clip_on=False, zorder=5, label='GDP')
cax3.scatter(China_counties[f'capacities_{t}_combined'], China_counties[f'production_{t}_combined'], s=40, alpha=.7, clip_on=False, zorder=5, label='POP-GDP')
cax3.plot([0, 60], [0, 60], ls='--', lw=1.5, c='red', zorder=5)
cax3.legend(loc='best', fontsize=9)
cax3.grid('on', ls='--', lw=0.5, ) 

cax3_1 = cax3.inset_axes([0.0, 1.0, 1.0, 0.2])
sns.histplot(China_counties[China_counties['capacities_2020_POP'] > 0]['capacities_2020_POP'].values, bins=np.linspace(0, 30, 31), color='lightgrey', kde=True, line_kws={'color':'grey'}, ax=cax3_1)
cax3_1.set(xticks=[], yticks=[], xlabel='', ylabel='count', xlim=(0, 30), ylim=(0, 300))
cax3_1.axis('off')

cax3_2 = cax3.inset_axes([1.0, 0.0, 0.2, 1.0])
# sns.histplot(y=China_counties[China_counties['capacities_2020'] > 0]['capacities_2020'].values, bins=np.linspace(0, 30, 31), kde=True, ax=cax3_2)
sns.histplot(y=China_counties[China_counties['production_2020_POP'] > 0]['production_2020_POP'].values, bins=np.linspace(0, 30, 31), alpha=0.3, kde=True, ax=cax3_2)
sns.histplot(y=China_counties[China_counties['production_2020_GDP'] > 0]['production_2020_GDP'].values, bins=np.linspace(0, 30, 31), alpha=0.3, kde=True, ax=cax3_2)
sns.histplot(y=China_counties[China_counties['production_2020_combined'] > 0]['production_2020_combined'].values, bins=np.linspace(0, 30, 31), alpha=0.3, kde=True, ax=cax3_2)
cax3_2.set(xticks=[], yticks=[], xlabel='', ylabel='', xlim=(0, 350), ylim=(0, 30))
cax3_2.axis('off')

cax4 = ax1.inset_axes([1.10, 0.05, 0.35, 0.35])
cax4.set(xlabel='reference value (Mt per year)', ylabel='predicted (Mt per year)', aspect=1.0, xlim=(0, 60), ylim=(0, 60))
sns.regplot(x=estimated_values_POP, y=reference_values, fit_reg=False, line_kws={'color':'r', 'zorder': 0}, scatter_kws={'alpha':0.7, 'clip_on': False, 'zorder':5}, label='POP', ax=cax4)
sns.regplot(x=estimated_values_GDP, y=reference_values, fit_reg=False, line_kws={'color':'r', 'zorder': 0}, scatter_kws={'alpha':0.7, 'clip_on': False, 'zorder':5}, label='GDP', ax=cax4)
sns.regplot(x=estimated_values_combined, y=reference_values, fit_reg=False, line_kws={'color':'r', 'zorder': 0}, scatter_kws={'alpha':0.7, 'clip_on': False, 'zorder':5}, label='POP-GDP', ax=cax4)
cax4.plot([0, 60], [0, 60], ls='--', lw=1.5, c='red', zorder=5)
cax4.legend(loc='best', fontsize=9)
cax4.grid('on', ls='--', lw=0.5, )

cax4_1 = cax4.inset_axes([0.0, 1.0, 1.0, 0.15])
sns.histplot(reference_values, bins=np.linspace(0, 60, 31), color='lightgrey', kde=True, line_kws={'color':'grey'}, ax=cax4_1)
cax4_1.set(xticks=[], yticks=[], xlabel='', ylabel='count', xlim=(0, 60), ylim=(0, 70))
cax4_1.axis('off')

cax4_2 = cax4.inset_axes([1.0, 0.0, 0.2, 1.0])
sns.histplot(y=estimated_values_POP, bins=np.linspace(0, 60, 31), alpha=0.3, kde=True, ax=cax4_2)
sns.histplot(y=estimated_values_GDP, bins=np.linspace(0, 60, 31), alpha=0.3, kde=True, ax=cax4_2)
sns.histplot(y=estimated_values_combined, bins=np.linspace(0, 60, 31), alpha=0.3, kde=True, ax=cax4_2)
cax4_2.set(xticks=[], yticks=[], xlabel='', ylabel='', xlim=(0, 150), ylim=(0, 60))
cax4_2.axis('off')

cax5 = ax1.inset_axes([0.05, 0.16, 0.25, 0.15])
sns.barplot(x=[i for i in range(7)], y=value_counts, width=0.7,  color='grey', ax=cax5)
cax5.set(xticks=[], yticks=[200, 400])
cax5.patch.set_alpha(0) 
cax5_spines = [spine for spine in cax5.spines.values()] 
cax5_spines[1].set_visible(False)
cax5_spines[3].set_visible(False)


# Coordinates of locations for circles (latitude, longitude)
locations_circle = {
    'Fanchang (Wuhu)': (1.47e6, 3.5e6),  # Example: Fanchang district, Wuhu city
    'Yingde (Qingyuan)': (1.04e6, 2.69e6),  # Yingde, Qingyuan city
    'Liyang (Changzhou)': (1.58e6, 3.54e6)  # Liyang, Changzhou city
}

# Draw circles
for location, coords in locations_circle.items():
    ax1.add_patch(Circle((coords[0], coords[1]), radius=8e4, color='red', fill=False, zorder=10))

ax1.annotate("Fanchang\n  (Wuhu)", xy=(1.5e6, 3.5e6-6e4), xytext=(2.0e6, 3.0e6), arrowprops=dict(arrowstyle="->", color='r'), zorder=10)
ax1.annotate("   Yingde\n(Qingyuan)", xy=(1.04e6+4e4, 2.69e6-6e4), xytext=(1.3e6, 2.0e6), arrowprops=dict(arrowstyle="->", color='r'), zorder=10)
ax1.annotate("    Liyang\n(Changzhou)", xy=(1.58e6+4e4, 3.54e6), xytext=(2.0e6, 3.6e6), arrowprops=dict(arrowstyle="->", color='r'), zorder=10)


fig.text(0.02, 0.80, 'a', fontsize=14, fontdict={'weight': 'semibold'})
fig.text(0.72, 0.80, 'b', fontsize=14, fontdict={'weight': 'semibold'})
fig.text(0.72, 0.44, 'c', fontsize=14, fontdict={'weight': 'semibold'})


plt.show()
fig.savefig('../figures/Fig_4.jpg', dpi=600, bbox_inches='tight')