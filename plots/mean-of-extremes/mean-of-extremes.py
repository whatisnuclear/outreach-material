import textwrap
import matplotlib.pyplot as plt

import numpy as np

bounds = [3.7, 12,110]

mu, sigma = bounds[1], 5

vals = [bounds[0]]+ list(np.random.normal(mu,sigma, 97)) + [bounds[2]]

vals = [bounds[0] if v<bounds[0] else v for v in vals]
vals = [bounds[2] if v>bounds[2] else v for v in vals]

mean = np.mean(vals)
median = np.median(vals)
mean_extreme =( min(vals) + max(vals)) /2.0

fig, ax = plt.subplots(dpi=200)

ax.bar(range(len(vals)), vals)

ax.axhline(y=mean, color="green")
ax.axhline(y=median, color="forestgreen")
ax.axhline(y=mean_extreme, color="red")

# Point out nuclear
ann = ax.annotate(f"'Mean of extremes': {mean_extreme:.1f}😛\nUsed by P. Dorfman to insinuate\nthat nuclear "
                "is bad for climate",
              xy=(11, mean_extreme), xycoords='data',
              xytext=(30, 80), textcoords='data',
              size=8, va="center", ha="center",
              bbox=dict(boxstyle="round4", fc="w"),
              arrowprops=dict(arrowstyle="-|>",
                              connectionstyle="arc3,rad=-0.2",
                              fc="w"),
              )

ann = ax.annotate(f"Mean: {mean:.1f}",
              xy=(20, mean), xycoords='data',
              xytext=(40, 45), textcoords='data',
              size=8, va="center", ha="center",
              bbox=dict(boxstyle="round4", fc="w"),
              arrowprops=dict(arrowstyle="-|>",
                              connectionstyle="arc3,rad=-0.2",
                              fc="w"),
              )

ann = ax.annotate(f"Median: {median:.1f}",
              xy=(60, median), xycoords='data',
              xytext=(70, 35), textcoords='data',
              size=8, va="center", ha="center",
              bbox=dict(boxstyle="round4", fc="w"),
              arrowprops=dict(arrowstyle="-|>",
                              connectionstyle="arc3,rad=-0.2",
                              fc="w"),
              )

ax.set_xlabel("Hypothetical study number")
ax.set_ylabel(r"Lifecycle CO$_{2}$-eq/kWh of nuclear **")

plt.title("The problem with the 'mean of the extremes'")

msg = f"""This plot demonstrates the problem with using the 'mean 
of the extremes' to express a dataset. The IPCC in 2014 published
a meta-analysis showing that nuclear's carbon emission studies showed
a minimum of {bounds[0]}, a median of {bounds[1]}, and a max of {bounds[2]}. If you just
take the mean of {bounds[0]:.1f}  and {bounds[2]:.1f} you get some overly high 
number ({mean_extreme:.1f}) but this totally misrepresents reality.

** I didn't have all 99 studies on hand when making this plot so the data itself
closely matches the real min/median/max but other than that is artificial to demonstrate
the problem with 'mean of the extremes'. Someone send me all 99 studies and I
will update. 
"""
fig.subplots_adjust(bottom=0.25,top=0.90)
ann = ax.text(0.1, 0.1, '\n'.join(textwrap.wrap(msg,130)),
              size=6, va="center", ha="left", transform=fig.transFigure
              )


# read image file
with open('huh.png', 'rb') as f:
    img = plt.imread(f, format='png')

# Draw image
axin = ax.inset_axes([60,70,25,37],transform=ax.transData)    # create new inset axes in data coordinates
axin.imshow(img)
axin.axis('off')


#plt.show()
plt.savefig('dorfman.png')
