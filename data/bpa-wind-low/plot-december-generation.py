"""
Plot load data from BPA 

https://transmission.bpa.gov/Business/Operations/Wind/default.aspx
"""

import datetime 

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mtick
import numpy as np
import pandas as pd

def load(fname, skiprows):
    print('Loading {}...'.format(fname))
    data1 = pd.read_excel(fname, "January-June", header=0, skiprows=range(skiprows))
    data2 = pd.read_excel(fname, "July-December", header=0, skiprows=range(skiprows))
    data = pd.concat([data1, data2])
    data = data.rename(columns={'TOTAL WIND GENERATION  IN BPA CONTROL AREA (MW; SCADA 79687)':'Wind', 
                                'TOTAL HYDRO GENERATION (MW; SCADA 79682)':'Hydro',
                                'TOTAL FOSSIL/BIOMASS GENERATION (MW; SCADA 16377)':'Fossil/Biomass',
                                'TOTAL NUCLEAR GENERATION (MW; 70681)':'Nuclear',
                                })
    data = data.set_index(pd.to_datetime(data['Date/Time']))
    data = data.dropna(thresh=len(data.columns)-4) # drop rows with all N/As
    return data

def plot_december(data):
    """Plot generation in BPA in the first half of December."""
    print('Plotting generation...')
    df = data['2017-12-01':'2017-12-25']
    #df = data['2017-07-01':'2017-12-16']
    fig, ax = plt.subplots()
    df = df[['Wind','Hydro','Nuclear','Fossil/Biomass']]
    df.plot(figsize=(10,8), ax=ax)
    plt.title('December 2017 Electricity Generation in the Bonnevile Power Administration Control Area')
    plt.xlabel('Day of month')
    plt.ylabel('Electricity Generation (Megawatts)')
    days = mdates.DayLocator()
    months = mdates.MonthLocator()
    hours = mdates.HourLocator()
    ax.xaxis.set_major_locator(days)
    #ax.xaxis.set_minor_locator(hours)
    ax.set_ybound(lower=0.0)
    plt.tight_layout()
    #plt.savefig('monthly_generation.png')
    plt.savefig('december_generation.png')

def getMonthLabel(dt):
    # matplotlib uses days since epoch (not seconds) so we convert here. 
    dt = mdates.num2date(dt)
    return dt.strftime('%B')

def plot_capacity(data, start = '2017-01-01', end = '2017-12-25', year = "2017"):
    """Plot wind capacity in BPA in the second half of 2017."""
    print('Plotting generation...')
    df = data[start:end]
    #df = data['2017-07-01':'2017-12-16']
    fig, ax = plt.subplots(figsize=(12,8),dpi=600)
    df = df[['Wind']]#,'Hydro','Nuclear','Fossil/Biomass']]
    x = np.array([di.to_pydatetime() for di in df.index])
    y = df.values.flatten()
    #capacity = 4000 # kind of a guess, goes higher sometimes but also is dynamic 
    capacity = max(y)
    cap_factor = sum(y) / (capacity*len(y))
    #df.plot.area(figsize=(12,8), ax=ax)
    ax.axhline(y=capacity,linestyle='--',color='red')
    ax.fill_between(x, y, capacity,label='Calm', color='lightblue', alpha=1.0, linewidth=0.2)
    ax.fill_between(x, 0, y, label='Windy', color='green', linewidth=0.2)
    plt.text(x[2000], capacity+20, 'Max capacity if all turbines were spinning',color='red')
    plt.text(x[1000], 4200, 'Approx. capacity factor: {:.0f}%'.format(cap_factor* 100))
    plt.title(f'Electricity Generation by Wind in the Bonnevile Power Administration Control Area ({year})')
    plt.ylabel('Electricity Generation from Wind (Megawatts)')
    plt.legend(loc='center right')
    #plt.fill(df.index, df.values, facecolor='blue', alpha=0.5)
    days = mdates.DayLocator()
    months = mdates.MonthLocator()
    hours = mdates.HourLocator()
    #ax.xaxis.set_major_locator(days)
    ax.xaxis.set_major_locator(months)
    ax.xaxis.set_minor_locator(days)
    ax.xaxis.set_major_formatter(mtick.FuncFormatter(lambda x,p:getMonthLabel(x)))
    ax.set_ybound(lower=0.0)
    ax.set_xbound(lower=min(x), upper=max(x))
    fig.tight_layout()
    #plt.savefig('monthly_generation.png')
    fig.savefig(f'wind_generation_{year}.png')

if __name__=='__main__':
    #data = load('WindGenTotalLoadYTD_2017.xls',21)
    #data = load('WindGenTotalLoadYTD_2019.xls',23)
    #data = load('WindGenTotalLoadYTD_2018.xls',23)
    data = load('WindGenTotalLoadYTD_2020.xls',23)
    #data = load('WindGenTotalLoadYTD_2017.xls')
    plot_capacity(data, start = '2020-01-01', end = '2020-10-17', year = "2020")
    #plot_december(data)
