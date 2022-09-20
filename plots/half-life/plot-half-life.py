"""A remake of my half-life plot b/c I can't find the source"""
import math

import matplotlib.pyplot as plt
from matplotlib.ticker import (MultipleLocator, AutoMinorLocator)
import numpy as np


years = np.arange(500)
half_lifes = [50,100,200,300]

N0=100.0

fig, ax = plt.subplots()
for hf in half_lifes:
    vals = N0*np.exp(-math.log(2)/hf*years)
    ax.plot(years, vals, label=f"Half-life = {hf} years")

    ax.arrow(
        hf, 50, 0, -50,
        head_width=10.0,
        head_length=3.0,
        fc="k",
        length_includes_head=True,
        ls="--"
    )

ax.arrow(0,50,300,0, ls="--")

ax.set_xlabel("Time since start of decay (years)")
ax.set_ylabel("Percentage of atoms remaining (%)")

ax.set_xlim(xmin=0,xmax=500)
ax.set_ylim(ymin=0,ymax=100)

ax.yaxis.set_major_locator(MultipleLocator(10))
ax.set_xticks([0,50,100,200,300,400,500])

ax.annotate('Halfway point',
            xy=(310, 50), xycoords='data',
            xytext=(30, 0), textcoords='offset points',
            arrowprops=dict(width=1.0, facecolor='black', shrink=0.05),
            horizontalalignment='left', verticalalignment='center')

ax.legend()
ax.grid(ls='--', alpha=0.2)
#ax.text(0.1, 0.8, 'CC-BY-NC whatisnuclear.com', 
#        fontsize=8, color='gray', alpha=0.3,
#        ha='center', va='center', rotation=0)
plt.title("Half life")
plt.tight_layout()
fig.savefig("half-life.svg")
    
    

