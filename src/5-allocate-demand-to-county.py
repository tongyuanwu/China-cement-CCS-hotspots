import numpy as np
import pandas as pd
import geopandas as gpd
import os
from matplotlib import pyplot as plt

names = locals()

future_national_cement_demand = pd.read_csv('../outputs/future_cement.csv', index_col=0)

def distribute_cement_demand(SSP, b):
    county_POP = pd.read_csv(os.path.join('..', 'outputs', f'China_county_population_{SSP}.csv'))
    county_GDP = pd.read_csv(os.path.join('..', 'outputs', f'China_county_GDP_{SSP}.csv'))

    county_POP.drop([176, 638, 639, 2403], inplace=True)
    county_GDP.drop([176, 638, 639, 2403], inplace=True)

    results = pd.DataFrame([], columns=['省', '市', '县', '县代码']+[t for t in range(2020, 2055, 5)])
    results[['省', '市', '县', '县代码']] = county_GDP[['省', '市', '县', '县代码']] 
    for t in range(2020, 2055, 5):
        total_GDP = county_GDP[f'GDP_{t}_{SSP}'].sum()
        total_POP = county_POP[f'POP_{t}_{SSP}'].sum()
        weight_POP = county_POP[f'POP_{t}_{SSP}'] / total_POP
        weight_GDP = county_GDP[f'GDP_{t}_{SSP}'] / total_GDP 
        weight_combined_ = b * weight_POP + (1 - b) * weight_GDP 
        weight_combined = weight_combined_ / np.sum(weight_combined_) 
        distributed_county_cement = future_national_cement_demand.loc[t, SSP] * weight_combined
        results[t] = np.nan
        results.loc[:, t] = distributed_county_cement * 1e3 

    return results

for i in range(1, 6):
    names[f'China_county_cement_POP_SSP{i}'] = distribute_cement_demand(f'SSP{i}', 1)
    names[f'China_county_cement_GDP_SSP{i}'] = distribute_cement_demand(f'SSP{i}', 0)
    names[f'China_county_cement_combined_SSP{i}'] = distribute_cement_demand(f'SSP{i}', 0.5)

for i in range(1, 6):
    names[f'China_county_cement_POP_SSP{i}'].to_csv(os.path.join('..', 'outputs', f'China_county_cement_POP_SSP{i}.csv'), index=False, encoding='utf-8-sig')
    names[f'China_county_cement_GDP_SSP{i}'].to_csv(os.path.join('..', 'outputs', f'China_county_cement_GDP_SSP{i}.csv'), index=False, encoding='utf-8-sig')
    names[f'China_county_cement_combined_SSP{i}'].to_csv(os.path.join('..', 'outputs', f'China_county_cement_combined_SSP{i}.csv'), index=False, encoding='utf-8-sig')