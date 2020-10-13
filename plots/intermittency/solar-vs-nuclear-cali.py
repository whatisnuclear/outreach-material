"""
Intermittency Graph by Nick Touran.

Goal here is to emphasize the complexities of daily and seasonal intermittency
compared to baseload low carbon sources like nuclear. 

Want two scenarios: nuclear and solar. For each, we'll want winter and summer versions. 
So, 2x2 subplots? With text in each one saying how much power going around.

Both nuclear and solar will just use some form of energy storage to deal with
intermittency and/or load follow
"""
import os
import csv
from datetime import datetime

import numpy as np
import matplotlib.pyplot as plt

from matplotlib.animation import ArtistAnimation
from matplotlib.animation import ImageMagickFileWriter
from matplotlib import collections

DFMT = "%m/%d/%Y %H:%M"
NUM_POINTS = 288  # b/c the data is messy


def read_data():
    """
    Read CAISO data

    Exported from web interface at https://www.caiso.com/TodaysOutlook/Pages/supply.html

    We need:
    * Summer demand
    * Winter demand
    * Summer solar (mostly shape important)
    * Winter solar (shape and peak/avg important for setting mag)
    * Nuclear generation (assume 91% cf)
    """
    data = {}
    data.update(_read_demand())
    data.update(_read_solar_supply())
    data.update(_read_nuclear_supply())
    return data


def _read_demand():
    """Read summer and winter demand curves."""
    data = {}
    for label, fname in [
        # ("Summer demand", "CAISO-demand-20200621.csv"),
        ("Summer demand", "CAISO-demand-20190621.csv"),
        ("Winter demand", "CAISO-demand-20191221.csv"),
    ]:
        datetimes = []
        print(f"opening {fname}")
        with open(os.path.join("data", fname)) as f:
            reader = csv.reader(f)
            row = next(reader)  # grab header
            # process row full of times
            date = row[0].split()[1]
            times = row[1:NUM_POINTS]
            # convert to datetime objects
            # import pdb;pdb.set_trace()
            datetimes = [datetime.strptime(f"{date} {time}", DFMT) for time in times]

            for row in reader:
                if row[0].startswith("Demand (5"):
                    # process demand data
                    print(f"Reading {label}")
                    mw = np.array([float(di) for di in row[1:NUM_POINTS]])
                    data[label] = datetimes, mw
                else:
                    # lookahead estimate. throw it away
                    print(f"Skipping {row[0]}")
                    continue
    return data


def _read_solar_supply():
    """Read how much solar comes in a day."""
    data = {}
    for label, fname in [
        ("Summer solar", "CAISO-renewables-20190621.csv"),
        ("Winter solar", "CAISO-renewables-20191221.csv"),
    ]:
        datetimes = []
        print(f"opening {fname}")
        with open(os.path.join("data", fname)) as f:
            reader = csv.reader(f)
            row = next(reader)  # grab header
            # process row full of times
            date = row[0].split()[1]
            times = row[1:NUM_POINTS]
            datetimes = [datetime.strptime(f"{date} {time}", DFMT) for time in times]

            for row in reader:
                if row[0].startswith("Solar"):
                    # process demand data
                    print(f"Reading {label}")
                    mw = np.array([float(di) for di in row[1:NUM_POINTS]])
                    data[label] = datetimes, mw
                else:
                    # lookahead estimate. throw it away
                    print(f"Skipping {row[0]}")
                    continue
    return data


def _read_nuclear_supply():
    return {}


def _integrate_megawatts(mw):
    """Sum megawatts over a day and return GW*day. Assume 5 minute increments."""
    mw = np.array(mw)
    return sum(mw * 5 / 60 / 24) / 1000


def plot_demand(data):
    """
    Plot demand curves

    I was surprised that winter 2019 was roughly the same demand integral as summer 2020.
    Maybe covid? So I grabbed summer 2019 data file too. Still really close!!

    Damn check out that huge baseload.
    """
    fig, ax = plt.subplots()
    for label in ["Summer demand", "Winter demand"]:
        x, y = data[label]
        integral = _integrate_megawatts(y)
        x = [dt.time().hour + dt.time().minute / 60 for dt in x]
        ax.plot(x, y / 1000, label=label + f" ({integral:.1f} GWd)")
    ax.legend(loc="lower right")
    ax.set_ylabel("Demand (GW)")
    ax.set_xlabel("Time (hour of day)")
    ax.set_title("Seasonal demand variation in California 2019")
    ax.grid(alpha=0.3, ls="--")
    ax.set_ylim(bottom=0)
    ax.set_xlim([0, 24])
    ax.set_xticks(np.arange(0, 25, 3.0))
    ax.text(1, 0.1, "W: 2019-12-21\nS: 2019-06-21\nData: CAISO")
    # plt.show()
    plt.savefig("Seasonal-demand-variation.png")


def plot_solar_supply(data):
    """Yikes solar was really low on 2019-12-21. Must've been cloudy."""
    fig, ax = plt.subplots()
    for label in ["Summer solar", "Winter solar"]:
        x, y = data[label]
        integral = _integrate_megawatts(y)
        x = [dt.time().hour + dt.time().minute / 60 for dt in x]
        ax.plot(x, y / 1000, label=label + f" ({integral:.1f} GWd)")
    ax.legend(loc="upper left")
    ax.set_ylabel("Solar supply (GW)")
    ax.set_xlabel("Time (hour of day)")
    ax.set_title("Seasonal solar variation in California 2019")
    ax.grid(alpha=0.3, ls="--")
    ax.set_ylim(bottom=0)
    ax.set_xlim([0, 24])
    ax.set_xticks(np.arange(0, 25, 3.0))
    ax.text(1, 0.1, "W: 2019-12-21\nS: 2019-06-21\nData: CAISO")
    # plt.show()
    plt.savefig("seasonal-solar-variation.png")


def plot_solar_scenario(data):
    fig, ax = plt.subplots(figsize=(10, 8))
    for season, color in [("Winter", "tab:cyan"), ("Summer", "tab:pink")]:
        demand_dt, demand_mw = data[f"{season} demand"]
        supply_dt, supply_mw = data[f"{season} solar"]
        demand_t = [dt.time().hour + dt.time().minute / 60 for dt in demand_dt]
        supply_t = [dt.time().hour + dt.time().minute / 60 for dt in supply_dt]
        demand_integral = _integrate_megawatts(demand_mw)
        supply_integral = _integrate_megawatts(supply_mw)
        scaleup = demand_integral / supply_integral

        ax.plot(
            demand_t,
            demand_mw / 1000,
            "-.",
            lw=2,
            color=color,
            label=f"{season} Demand ({demand_integral:.1f} GWd)",
        )
        ax.plot(
            supply_t,
            supply_mw / 1000,
            "-",
            lw=2,
            color=color,
            label=f"{season} Supply Current ({supply_integral:.1f} GWd)",
        )
        ax.plot(
            supply_t,
            scaleup * supply_mw / 1000,
            ":",
            lw=2,
            color=color,
            label=f"{season} Supply Required ({supply_integral*scaleup:.1f} GWd)",
        )

    ax.legend(loc="upper left")
    ax.set_ylabel("Power (GW)")
    ax.set_xlabel("Time (hour of day)")
    ax.set_title("Seasonal implications of 100% solar in California")
    ax.grid(alpha=0.3, ls="--")
    ax.set_ylim(bottom=0)
    ax.set_xlim([0, 24])
    ax.set_xticks(np.arange(0, 25, 3.0))
    ax.text(1, 5, "W: 2019-12-21\nS: 2019-06-21\nData: CAISO")
    # plt.show()
    plt.savefig("solar-scenario.png")

def plot_summer_scenario(data):
    """Just do summer."""
    #seasons = ["Winter", "Summer"]
    seasons = ["Winter"]
    fig, axs = plt.subplots(1, len(seasons), figsize=(8*len(seasons), 8), squeeze=False)
    for season, ax in zip(seasons,axs[0]):
        #ax = ax[0]
        demand_dt, demand_mw = data[f"{season} demand"]
        supply_dt, supply_mw = data[f"{season} solar"]
        demand_t = [dt.time().hour + dt.time().minute / 60 for dt in demand_dt]
        supply_t = [dt.time().hour + dt.time().minute / 60 for dt in supply_dt]
        demand_integral = _integrate_megawatts(demand_mw)
        supply_integral = _integrate_megawatts(supply_mw)
        scaleup = demand_integral / supply_integral
        demand = ax.plot(
            demand_t,
            demand_mw / 1000,
            "-",
            lw=2,
            color="red",
            label=f"{season} Demand ({demand_integral:.1f} GWd)",
        )
        demand_fill = ax.fill_between(demand_t, demand_mw/1000, y2=0, alpha=1.0, color="tan" )
        demand_lab = ax.text(3, 10, f"Demand:\n{demand_integral:.1f} GWd",
                horizontalalignment='center',
                verticalalignment='center',
                )
 
        #import pdb; pdb.set_trace()
        supply = ax.plot(
            supply_t,
            supply_mw / 1000,
            "-",
            lw=2,
            color="green",
            label=f"{season} Supply Current ({supply_integral:.1f} GWd)",
        )
        supply_fill=ax.fill_between(demand_t, supply_mw/1000, y2=0, alpha=1.0, color="green")
        supply_lab = ax.text(12, 3, f"Current Supply:\n{supply_integral:.1f} GWd",
                horizontalalignment='center',
                verticalalignment='center',
                )

        supply_scaled = ax.plot(
            supply_t,
            scaleup * supply_mw / 1000,
            "--",
            lw=2,
            color="green",
            label=f"{season} Supply Required ({supply_integral*scaleup:.1f} GWd)",
        )
        supply_scaled_fill = ax.fill_between(demand_t, scaleup*supply_mw/1000, y2=0, alpha=0.2, color="green",
                hatch=".")
        supply_scaled_lab = ax.text(12, 40, f"Required Supply:\n{supply_integral*scaleup:.1f} GWd",
                horizontalalignment='center',
                verticalalignment='center',
                )


        an_demand1 = ax.annotate('Area of supply must\nequal area of demand',
            xy=(9, 5),  
            xytext=(1, 40), 
            arrowprops=dict(facecolor='black', shrink=0.05),
            horizontalalignment='left',
            verticalalignment='bottom',
            )

        an_demand2 = ax.annotate('Area of supply must\nequal area of demand',
            xy=(4, 15),  
            xytext=(1, 40), 
            arrowprops=dict(facecolor='black', shrink=0.05),
            horizontalalignment='left',
            verticalalignment='bottom',
            )

        an_demand3 = ax.annotate('Area of supply must\nequal area of demand',
            xy=(10, 40),
            xytext=(1, 40), 
            arrowprops=dict(facecolor='black', shrink=0.05),
            horizontalalignment='left',
            verticalalignment='bottom',
            )

        an_storage = ax.annotate('Area above red demand\ncurve must be handled \nby energy storage systems',
            xy=(16, 60),  
            xytext=(17, 70), 
            arrowprops=dict(facecolor='black', shrink=0.05),
            horizontalalignment='left',
            verticalalignment='bottom',
     )

        peak_req = max(supply_mw*scaleup/1000)
        storage_bounds = ax.annotate("", xy=(15.8, 24), xytext=(15.8, peak_req),
                 arrowprops=dict(arrowstyle="<->"))

        if ax is axs[0][0]:
            # winter only
            an_cap_req = ax.annotate(f'Total capacity required\n({peak_req:.1f}) GW',
                xy=(11, peak_req),  
                xytext=(4, peak_req), 
                arrowprops=dict(facecolor='black', shrink=0.05),
                horizontalalignment='center',
                verticalalignment='center',
                )

            cpeak = max(supply_mw/1000)
            an_cap_now = ax.annotate(f'Current winter capacity\n({cpeak:.1f}) GW',
                xy=(13, cpeak),  
                xytext=(20, cpeak), 
                arrowprops=dict(facecolor='black', shrink=0.05),
                horizontalalignment='center',
                verticalalignment='center',
                )

        #ax.legend(loc="upper left")
        ax.set_ylabel("Power (GW)")
        ax.set_xlabel("Time (hour of day)")
        ax.grid(alpha=0.3, ls="--")
        ax.set_ylim(bottom=0)
        ax.set_xlim([0, 24])
        ax.set_ylim([0, 120])
        ax.set_xticks(np.arange(0, 25, 3.0))

    fig.suptitle("Seasonal implications of 100% solar in California")
    #ax.text(1, 5, "W: 2019-12-21\nS: 2019-06-21\nData: CAISO")


    scene = []
    frames = []

    scene=[demand[0], demand_fill, demand_lab]
    frames.append(scene[:])
    scene.extend([supply[0], supply_fill, supply_lab])
    frames.append(scene[:])
    scene.extend([an_demand2, an_demand1])
    frames.append(scene[:])
    scene.extend([supply_scaled[0], supply_scaled_fill, supply_scaled_lab, an_demand3])
    scene.remove(an_demand1)
    frames.append(scene[:])
    scene.remove(an_demand3)
    scene.remove(an_demand2)
    scene.extend([an_cap_now, an_cap_req])
    frames.append(scene[:])
    scene.extend([an_storage, storage_bounds])
    frames.append(scene[:])

    anim = ArtistAnimation(fig,frames) 

    from matplotlib.animation import FFMpegWriter
    writer = FFMpegWriter(fps=1, metadata=dict(artist='Me'), bitrate=1800)
    anim.save("movie.mp4", writer=writer)
    #writer = ImageMagickFileWriter()
    #anim.save("animation.avi", writer=writer)



    #plt.show()



if __name__ == "__main__":
    data = read_data()
    #plot_demand(data)
    #plot_solar_supply(data)
    #plot_solar_scenario(data)
    plot_summer_scenario(data)
