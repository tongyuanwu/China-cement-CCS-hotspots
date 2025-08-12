import numpy as np
import pandas as pd 
from scipy.optimize import curve_fit
from matplotlib import pyplot as plt

DF = pd.read_excel('../data/20241121.xlsx', index_col=0)

def predict_future_cement_consumption_per_cap(gdp):
    def gaussian(x, a, b, c):
        return a * np.exp(-((x - b) / c) ** 2)
    
    def gradual_decline(gdp, current_gdp, current, target, decay):
        return target + (current - target) * np.exp(-decay * (gdp - current_gdp))

    popt, _ = curve_fit(gaussian, X, Y, p0=initial_guesses)

    current_gdp = X[2020] 
    current_consumption = gaussian(current_gdp, *popt)  # Current per-capita consumption (t/year)
    target_gdp = 60000  # Target per-capita GDP
    target_consumption = 0.522  # Saturation level 
    gg = np.where(gdp <= current_gdp, gaussian(gdp, *popt), gradual_decline(gdp, current_gdp, current_consumption, target_consumption, 0.00010))

    return gg 


# Fit the logistic curve
X = DF.loc[[t for t in range(1980, 2025, 5)], 'per-capita GDP (2017 int. dollars)_OECD_historical']
Y = DF.loc[[t for t in range(1980, 2025, 5)], 'per-capita consumption_2 (t/yr)']

# Initial guesses for parameters (adjust as necessary)
initial_guesses = [1.5, 10000, 5000]


future_GDP_pc = pd.DataFrame([], index=[t for t in range(1980, 2061)], columns=[f'SSP{i}' for i in range(1, 6)]).astype('float')
future_pop = pd.DataFrame([], index=[t for t in range(1980, 2061)], columns=[f'SSP{i}' for i in range(1, 6)]).astype('float')
future_cement_pc = pd.DataFrame([], index=[t for t in range(1980, 2061)], columns=[f'SSP{i}' for i in range(1, 6)])

for i in range(1, 6):
    future_GDP_pc.loc[1980:2020, f'SSP{i}'] = DF.loc[1980:2020, 'per-capita GDP (2017 int. dollars)_OECD_historical'].interpolate()
    future_GDP_pc.loc[2020:2060, f'SSP{i}'] = DF.loc[2020:2060, f'per-capita GDP_SSP{i}'].interpolate()
    future_pop.loc[1980:2020, f'SSP{i}'] = DF.loc[1980:2020, 'population_IIASA_WiC_historical (million)'].interpolate()
    future_pop.loc[2020:2060, f'SSP{i}'] = DF.loc[2020:2060, f'population_SSP{i}'].interpolate()


future_GDP_pc = future_GDP_pc.round(2)
future_pop = future_pop.round(3)

future_cement_pc.loc[:, :] = predict_future_cement_consumption_per_cap(future_GDP_pc.loc[1980:2060].values)


future_cement = pd.DataFrame([], index=[t for t in range(1980, 2061)], columns=[f'SSP{i}' for i in range(1, 6)])
future_cement.loc[:, :] = future_pop.loc[1980:2060].values * future_cement_pc.loc[1980:2060].values

error = pd.DataFrame([], index=[t for t in range(1990, 2025)])
error['model'] = 100 *(future_cement.loc[1990:2024, 'SSP2'] - DF.loc[1990:2024, 'cement consumption (Mt)']) / DF.loc[1990:2024, 'cement consumption (Mt)']


future_cement.loc[2020:].to_csv('../outputs/future_cement.csv')     # output and save the results, unit: Million tons (Mt)


fig = plt.figure(figsize=(6.5, 4), constrained_layout=True)

ax1 = plt.subplot(1, 1, 1)
ax1_1 = ax1.twinx()
future_cement.loc[:, 'SSP2'].plot(ls='--', label='predicted', zorder=10, ax=ax1)
ax1.fill_between(np.linspace(2024, 2050, 27), future_cement.loc[2024:2050, 'SSP5'].values.astype(float), future_cement.loc[2024:2050, 'SSP3'].values.astype(float), color='lightgrey')
ax1.scatter(x=DF.loc[:2024, ].index.values, y=DF.loc[:2024, 'cement consumption (Mt)'].values, s=10, c='none', ec='grey', marker='o', zorder=11, label='observed')
ax1.set(xlim=(1989.2, 2050), ylim=(-600, 3000), ylabel='Mt/year', xticks=[t for t in range(1990, 2055, 5)], yticks=[i*600 for i in range(6)], )
ax1.tick_params(axis='x', length=0)
ax1.legend()
ax1.grid('on', lw=0.5, ls='--') 

ax1_1.bar([t for t in range(1990, 2025)], error['model'].values, color='r', alpha=0.3, zorder=9)
ax1_1.hlines(0, -5, 35, ls='--', lw=0.5, color='r', zorder=10)
ax1_1.set(ylim=(-20, 100), yticks=[-20, -10, 0, 10, 20, 40, 60, 80, 100])
ax1_1.set_yticklabels([-20, -10, 0, 10, 20, 40, 60, 80, 100], color='r')
ax1_1.set_ylabel('error (%)', color='r')
ax1_1.grid('on', lw=0.5, ls='--')

plt.show()
fig.savefig('../figures/Fig_2.jpg', dpi=600, bbox_inches='tight')