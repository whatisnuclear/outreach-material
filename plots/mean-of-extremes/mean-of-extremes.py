import textwrap
import matplotlib.pyplot as plt

import numpy as np


def generateData():
    bounds = [3.7, 12,110]

    mu, sigma = bounds[1], 5

    vals = [bounds[0]]+ list(np.random.normal(mu,sigma, 97)) + [bounds[2]]

    vals = [bounds[0] if v<bounds[0] else v for v in vals]
    vals = [bounds[2] if v>bounds[2] else v for v in vals]
    
    return range(len(vals)), vals

def plot(labels, vals):

    maxData = max(vals)
    minData = min(vals)

    mean = np.mean(vals)
    median = np.median(vals)
    mean_extreme =( min(vals) + max(vals)) /2.0

    fig, ax = plt.subplots(dpi=200)

    ax.bar(range(len(vals)), vals)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, size=4, rotation='vertical')

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

    ax.set_xlabel("Study considered in Yale meta-analysis")
    ax.set_ylabel(r"Lifecycle CO$_{2}$-eq/kWh of nuclear (harmonized)")

    plt.title("The problem with the 'mean of the extremes'")

    msg = f"""This plot demonstrates the problem with using the 'mean 
of the extremes' to express a dataset. Yale in 2012 published
a meta-analysis showing that nuclear's carbon emission studies showed
a minimum of {minData}, a median of {median}, and a max of {maxData}. If you just
take the mean of {minData:.1f}  and {maxData:.1f} you get some overly high 
number ({mean_extreme:.1f}) but this totally misrepresents reality.

Data shown is the harmonized column from Yale supplement: https://onlinelibrary.wiley.com/action/downloadSupplement?doi=10.1111%2Fj.1530-9290.2012.00472.x&file=JIEC_472_sm_suppmat.pdf

    """
    fig.subplots_adjust(bottom=0.35,top=0.90)
    ann = ax.text(0.1, 0.1, '\n'.join(textwrap.wrap(msg,130)),
                  size=6, va="center", ha="left", transform=fig.transFigure
                  )


    # read image file
    with open('huh.png', 'rb') as f:
        img = plt.imread(f, format='png')

    # Draw image
    axin = ax.inset_axes([80,70,25,37],transform=ax.transData)    # create new inset axes in data coordinates
    axin.imshow(img)
    axin.axis('off')


    #plt.show()
    plt.savefig('dorfman.png')

def readFile():
    studies = read()
    labels = list(studies.keys())
    vals = list(studies.values())
    return labels, vals

def read():
    # read data table from https://onlinelibrary.wiley.com/action/downloadSupplement?doi=10.1111%2Fj.1530-9290.2012.00472.x&file=JIEC_472_sm_suppmat.pdf
    studies = {}
    counts={}
    with open("yale-nuclear-co2-table.txt") as f:
        for line in f:
            vals = line.split()
            baselabel = ' '.join(vals[:2])
            count = counts.get(baselabel,0) +1
            label = f"{baselabel}_{count}"
            counts[baselabel]=count
            studies[label] = float(vals[9])
    return studies

if __name__=="__main__":
    labels, vals = readFile()
    plot(labels, vals)
