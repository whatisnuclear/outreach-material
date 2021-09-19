import os

import pandas as pd
from pandas import ExcelWriter
from pandas import ExcelFile

import matplotlib.pyplot as plt

df = pd.read_excel(os.path.join('..','data','Table_8.1_Nuclear_Energy_Overview.xlsx'), sheet_name='Nick')
dates = [d.to_pydatetime() for d in df["Month"]]
endyear = dates[-1].year
cf = df["Nuclear Generating Units, Capacity Factor"]
avg = cf.rolling(12).mean()
fig, ax = plt.subplots(figsize=(11,7))
ax.bar(dates, cf, width=31, color='lightskyblue', label="Monthly")
ax.xaxis_date()
ax.plot(dates, avg, 'k',label="Avg")

ax.set_title(f"US Nuclear Power Plant Capacity Factors through {endyear}",fontsize=16)
ax.set_ylabel("Capacity Factor (%)")
ax.autoscale(enable=True, axis='x', tight=True)
ax.yaxis.grid(which="major", linestyle='--', alpha=0.5)
ax.legend()

ann = ax.text(0.14, 0.13, "Data from EIA Annual Energy Review\nhttps://www.eia.gov/totalenergy/data/annual/",
              size=8, va="center", ha="left", transform=fig.transFigure,
              alpha=0.7
              )

ann = ax.text(0.72, 0.13, "CC-BY-NC whatisnuclear.com",
              size=8, va="center", ha="left", transform=fig.transFigure,
              alpha=0.7
              )

#plt.show()
plt.savefig("nuclear-capacity-factors-2019.png")

