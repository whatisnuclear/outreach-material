"""Plot capacity factors."""

import os
from operator import itemgetter
import textwrap
import datetime

import yaml
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.dates import date2num
import matplotlib.dates as mdates
import matplotlib.patches as mpatches
from matplotlib.collections import PatchCollection

ISOFMT = "%Y-%M-%d"

def load(fname=os.path.join('..','data','pdrp.yaml')):
    with open(fname) as f:
        data = yaml.load(f)
    return data["reactors"]

def dt(date):
    """convert date to datetime at midnight for easier plotting"""
    return date2num(datetime.datetime(date.year, date.month, date.day))

colors = {
        "BWR": "blue"
        }

DOTWIDTH= 130
LINEHEIGHT = 0.1
STARTYEAR = 1951
ENDYEAR=1977

def plot(data, fname='power-demonstration-reactor-program.png'):

    fig, ax = plt.subplots(figsize=(16,14))

    bars = []
    reactors = []
    filteredRx = {}
    for reactor, rxdata in data.items():
        if "contracted" not in rxdata:
            print(f"skipping {reactor}")
            continue
        filteredRx[reactor]=rxdata

    # sort by first two available dates (often solicited/contracted)
    for reactor, rxdata in sorted(
            filteredRx.items(), 
            key = lambda kv: (kv[1].get("solicited", kv[1]["contracted"]), kv[1].get("contracted")),reverse=True):
        print(f"adding {reactor}")
        reactors.append(reactor)
        patches = []

        contracted = dt(rxdata["contracted"])
        y = len(reactors)
        if "solicited" in rxdata:
            # planning period between solicitation and contract
            solicited = dt(rxdata["solicited"])
            patches.append(mpatches.Ellipse((solicited,y), DOTWIDTH, 0.25, facecolor="green", edgecolor="k",
                lw=LINEHEIGHT, alpha=0.5))
            bar = ax.barh(y, contracted-solicited, left=solicited, height=LINEHEIGHT, color="green", alpha=0.2)
            start = solicited
        else:
            # well it was at least contracted
            start=contracted

        patches.append(mpatches.Ellipse((contracted,y), DOTWIDTH, 0.25, fill=False,
            edgecolor="green",
            lw=1.0, alpha=1.0))

        #patches.append(mpatches.Ellipse((contracted,y), DOTWIDTH, 0.25, facecolor="green", edgecolor="k", lw=0.2))
        ax.annotate(f'{reactor} {rxdata["type"]} in {rxdata["location"]} ({rxdata.get("MWe","-")} MW$_e$)',
                    xy=(start, y),
                    xytext=(5, 8),  
                    textcoords="offset points",
                    ha='left', va='bottom', size=17)

        if "ground broken" in rxdata:
            # planning period between contract and groundbreaking
            groundbroken = dt(rxdata["ground broken"])
            #patches.append(mpatches.Ellipse((groundbroken,y), DOTWIDTH, 0.25, facecolor="brown",
            #edgecolor="k", lw=LINEHEIGHT, alpha=1.0))
            ax.barh(y, groundbroken-contracted, left=contracted, height=LINEHEIGHT, color="green", alpha=0.4)

            # Between construction and critical
            critical = dt(rxdata["critical"])
            patches.append(mpatches.Ellipse((critical,y), DOTWIDTH, 0.25, facecolor="blue", edgecolor="k",
                lw=LINEHEIGHT, alpha=0.5))
            bar = ax.barh(y, critical-groundbroken, left=groundbroken, height=LINEHEIGHT, color="green", alpha=0.6)

            # Between critical and commercial
            fullpower = dt(rxdata["fullpower"])
            #patches.append(mpatches.Ellipse((fullpower,y), DOTWIDTH, 0.25, facecolor="blue", edgecolor="k", lw=0.2, alpha=1.0))
            bar = ax.barh(y, fullpower-critical, left=critical, height=LINEHEIGHT, color="green", alpha=0.8)

            # Commercial operation to shutdown
            shutdown = dt(rxdata["shutdown"])
            patches.append(mpatches.Ellipse((shutdown,y), DOTWIDTH, 0.25, facecolor="k", edgecolor="k", lw=0.2))
            ax.barh(y, shutdown-fullpower, left=fullpower, height=LINEHEIGHT, color="green", alpha=1.0)

            if rxdata["shutdown"].year > ENDYEAR:
                # add overflow label
                labeltime = dt(datetime.datetime(ENDYEAR-2, 6, 1))
                ax.annotate(f'{rxdata["shutdown"].year} →',
                            xy=(labeltime, y),
                            xytext=(5, 8),  
                            textcoords="offset points",
                            ha='left', va='bottom', size=14)

        # Do at the end so milestones are on top
        for patch in patches:
            ax.add_patch(patch)

    # Make custom legend defining the milestone markers
    legendElements = [
        mpatches.Ellipse((0,0), DOTWIDTH, 0.25, facecolor="green", edgecolor="k", lw=LINEHEIGHT, alpha=0.5,
        label="Solicited"),
        mpatches.Ellipse((0,0), DOTWIDTH, 0.25, fill=False, edgecolor="green", lw=1.0, alpha=1.0, label="Contracted"),
        mpatches.Ellipse((0,0), DOTWIDTH, 0.25, facecolor="blue", edgecolor="k", lw=LINEHEIGHT, alpha=0.5,
        label="Critical"),
        mpatches.Ellipse((0,0), DOTWIDTH, 0.25, facecolor="k", edgecolor="k", lw=0.2, label="Shutdown"),
    ]
    ax.legend(handles=legendElements, fontsize=16)

    ax.set_yticks(range(1,len(reactors)+1))
    ax.get_yaxis().set_visible(False)
   
    ax.xaxis_date()
    # show each year on axis
    ax.xaxis.set_major_locator(mdates.YearLocator(5))
    ax.xaxis.set_minor_locator(mdates.YearLocator())
    #ax.set_yticklabels(reactors)
    plt.title("The Power Demonstration Reactor Program", fontsize=16)
    #ax.set_ylim([0,900]) # make room for data label
    ax.set_xlim([date2num(datetime.datetime(STARTYEAR,1,1)),
                 date2num(datetime.datetime(ENDYEAR,1,1))])
    ax.xaxis.tick_top()
    #ax.xaxis.set_label_position('bottom')
    ax.tick_params(direction="in", labelsize=14)

    # Manually squish the subplot to make room for labels
    fig.subplots_adjust(bottom=0.05, top=0.95, left=0.05, right=0.95)
    ann = ax.text(0.76, 0.06, '\n'.join(textwrap.wrap( "CC-BY-NC whatisnuclear.com",130)),
                  size=12, va="center", ha="left", transform=fig.transFigure,
                  alpha=0.7
                  )

    if fname:
        plt.savefig(fname)
    else:
        plt.show()

if __name__ == '__main__':
    data = load()
    plot(data)
