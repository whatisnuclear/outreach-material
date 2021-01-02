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
import copy

import numpy as np
import matplotlib.pyplot as plt

import matplotlib
matplotlib.use('TkAgg') 
from matplotlib import animation
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


import typing


class Data(typing.NamedTuple):
    time: np.ndarray
    vals: np.ndarray
    integral: np.ndarray
    label: str
    color: str
    hatch: str = None
    opacity: float = 1.0


def process(data, season, nonelectric=False):
    demand_dt, demand_mw = data[f"{season} demand"]
    demand_integral = _integrate_megawatts(demand_mw)
    demand_gw = demand_mw/1000
    demand_t = np.array([dt.time().hour + dt.time().minute / 60 for dt in demand_dt])
    demand = Data(demand_t, demand_gw, demand_integral, f"{season} demand", "tan")

    # factor in other 60% that is not electric
    # gratuitously reduce primary energy assuming electric efficiency
    # by 60%
    total_integral = demand_integral / 0.40 * 0.6
    others_integral = (1-0.4)*total_integral  # oops had 0.6 down here earlier
    # flat line value in GW will equal integral in GWd since time is 1 day
    others_gw = np.array([others_integral for dt in demand_dt])
    others = Data(demand_t, others_gw, others_integral, "Transportation,Industry,Heating", "brown")

    supply_dt, supply_mw = data[f"{season} solar"]
    supply_t = np.array([dt.time().hour + dt.time().minute / 60 for dt in supply_dt])
    supply_integral = _integrate_megawatts(supply_mw)
    supply_gw = supply_mw/1000
    supply = Data(
        supply_t, supply_gw, supply_integral, f"{season} solar supply", "green"
    )

    if nonelectric:
        factor = total_integral/supply_integral
    else:
        factor = demand_integral /supply_integral
    scaled_gw = supply_gw * factor
    scaled = Data(
        supply_t,
        scaled_gw,
        supply_integral*factor,
        f"{season} required supply",
        "green",
        "",
        0.1,
    )
    return demand, supply, scaled, others


def add_data(ax, data, x=12, y0=0.0):
    line, = ax.plot(
        data.time,
        data.vals,
        "-",
        lw=2,
        color=data.color,
        label=f"{data.label} ({data.integral:.1f} GWd)",
    )

    fill = ax.fill_between(
        data.time, data.vals, y2=y0, alpha=data.opacity, color=data.color, hatch=data.hatch
    )
    text = ax.text(
        x,
        data.vals.max()*0.6,
        f"{data.label}:\n{data.integral:.1f} GWd",
        horizontalalignment="center",
        verticalalignment="center",
    )
    return line, fill, text





def plot_both_scenarios(data):
    seasons = ["Summer", "Winter"]
    #seasons = ["Winter"]
    fig, axs = plt.subplots(
        1, len(seasons), figsize=(4 * len(seasons), 4), squeeze=False, dpi=100
    )
    for season, ax in zip(seasons, axs[0]):
        demand, supply, scaled, _others = process(data, season)
        add_data(ax, demand)
        add_data(ax, supply)
        add_data(ax, scaled)


        an_demand1 = ax.annotate(
            "Area of supply\nmust equal area\nof demand",
            xy=(8, 5),
            xytext=(4, 50),
            arrowprops=dict(arrowstyle="->",facecolor="black",  relpos=(0.3,0.5)),
            horizontalalignment="center",
            verticalalignment="bottom",
        )

        an_demand2 = ax.annotate(
            "Area of supply\nmust equal area\nof demand",
            xy=(4, 15),
            xytext=(4, 50),
            arrowprops=dict(arrowstyle="->",facecolor="black",  relpos=(0.3,0.5)),
            horizontalalignment="center",
            verticalalignment="bottom",
        )

        #an_demand3 = ax.annotate(
        #    "Area of supply must\nequal area of demand",
        #    xy=(10, 40),
        #    xytext=(1, 40),
        #    arrowprops=dict(facecolor="black", shrink=0.05),
        #    horizontalalignment="left",
        #    verticalalignment="bottom",
        #)

        if ax is axs[0][0]:
            an_storage = ax.annotate(
                "Area above demand\ncurve must be handled \nby energy storage\nsystems",
                xy=(16, 60),
                horizontalalignment="left",
                verticalalignment="bottom",
            )

            peak_req = scaled.vals.max()
            storage_bounds = ax.annotate(
                "",
                xy=(18, 24),
                xytext=(18, peak_req),
                arrowprops=dict(arrowstyle="<->"),
            )

        if ax is axs[0][1]:
            # winter only
            peak_req = scaled.vals.max()
            an_cap_req = ax.annotate(
                f"Total capacity required\n({peak_req:.1f}) GW",
                xy=(14, peak_req),
                xytext=(20, peak_req),
                arrowprops=dict(facecolor="black", shrink=0.05),
                horizontalalignment="center",
                verticalalignment="center",
            )

            cpeak = supply.vals.max()
            an_cap_now = ax.annotate(
                f"Current winter capacity\n({cpeak:.1f}) GW",
                xy=(14, cpeak),
                xytext=(20, cpeak),
                arrowprops=dict(facecolor="black", shrink=0.05),
                horizontalalignment="center",
                verticalalignment="center",
            )

        add_axes(ax)
        ax.set_title(f"{season}")
    #fig.suptitle("Seasonal implications of 100% solar in California", fontsize=14)
    # ax.text(1, 5, "W: 2019-12-21\nS: 2019-06-21\nData: CAISO")

    #plt.tight_layout()
    plt.show()
    #plt.savefig("solar-intermittency.png")



    #from matplotlib.animation import FFMpegWriter

    #writer = FFMpegWriter(fps=1, metadata=dict(artist="Me"), bitrate=1800)
    #anim.save("movie.mp4", writer=writer)
    # writer = ImageMagickFileWriter()
    # anim.save("animation.avi", writer=writer)

def scene1_summer(season, data, showSupply=True):
    fig, axs = plt.subplots(1, 1,  squeeze=False, dpi=200)
    ax = axs[0][0]
    demand, supply, scaled, others = process(data, season)
    add_data(ax, demand, 3.5)
    if showSupply:
        add_data(ax, supply, 13)
    #add_data(ax, scaled)


    #an_demand1 = ax.annotate(
    #    "Area of supply\nmust equal area\nof demand",
    #    xy=(8, 5),
    #    xytext=(4, 30),
    #    arrowprops=dict(arrowstyle="->",facecolor="black",  relpos=(0.3,0.5)),
    #    horizontalalignment="center",
    #    verticalalignment="bottom",
    #)

    #an_demand2 = ax.annotate(
    #    "Area of supply\nmust equal area\nof demand",
    #    xy=(4, 15),
    #    xytext=(4, 30),
    #    arrowprops=dict(arrowstyle="->",facecolor="black",  relpos=(0.3,0.5)),
    #    horizontalalignment="center",
    #    verticalalignment="bottom",
    #)

    ax.set_title(f"{season} electricity in California")
    #fig.suptitle("Seasonal implications of 100% solar in California", fontsize=14)
    # ax.text(1, 5, "W: 2019-12-21\nS: 2019-06-21\nData: CAISO")

    ax.set_ylabel("Power (GW)")
    ax.set_xlabel("Time (hour of day)")
    ax.grid(alpha=0.3, ls="--")
    ax.set_ylim(bottom=0)
    ax.set_xlim([0, 24])
    ax.set_ylim([0, 40])
    ax.set_xticks(np.arange(0, 25, 3.0))

    #plt.tight_layout()
    #plt.show()
    if showSupply:
        dmf=""
    else:
        dmf="demand-"
    plt.savefig(f"solar-intermittency-scene1-{dmf}{season}.png")


def scene2_scaleup(season, data, nonelectric=False):
    """Animate the scaleup"""
    FRAMES = 100
    def scaleFactor():
        for frac in np.linspace(0,1,FRAMES):
            print(frac)
            yield frac

    fig, axs = plt.subplots( 1, 1,  squeeze=False, dpi=200)
    ax= axs[0][0]
    ax.set_ylabel("Power (GW)")
    ax.set_xlabel("Time (hour of day)")
    ax.grid(alpha=0.3, ls="--")
    ax.set_ylim(bottom=0)
    ax.set_xlim([0, 24])
    ax.set_ylim([0, 70 if nonelectric else 40])
    ax.set_xticks(np.arange(0, 25, 3.0))
    demand, supply, scaled, others = process(data, season, nonelectric)
    if nonelectric:
        add_data(ax, others, x=6.5)
        demand = Data(demand.time, demand.vals + others.vals, demand.integral,
                "Electricity", demand.color, demand.hatch, demand.opacity)
        add_data(ax, demand, x=3.5, y0=others.vals.max())
    else:
        add_data(ax, demand, x=3.5)
    data=supply
    line1, = ax.plot(
        data.time,
        data.vals,
        "--",
        lw=2,
        color=data.color,
        label=f"{data.label} ({data.integral:.1f} GWd)",
    )
    line, = ax.plot(
        data.time,
        data.vals,
        "-",
        lw=2,
        color=data.color,
        label=f"{data.label} ({data.integral:.1f} GWd)",
    )

    fill1 = ax.fill_between(
        data.time, data.vals, y2=0, alpha=data.opacity, color=data.color, hatch=data.hatch
    )
    text1 = ax.text(
        13,
        data.vals.max()*0.6,
        f"{data.label}:\n{data.integral:.1f} GWd",
        horizontalalignment="center",
        verticalalignment="center",
    )
    global fill
    fill = ax.fill_between(
        data.time, data.vals, y2=0, alpha=data.opacity, color=data.color, hatch=data.hatch
    )
    text = ax.text(
        13,
        data.vals.max()*0.6,
        f"{data.label}:\n{data.integral:.1f} GWd",
        horizontalalignment="center",
        verticalalignment="center",
    )

    ax.set_title(f"{season} electricity in California")

    def run(frac):
        global fill
        y = supply.vals*(1-frac)+scaled.vals*frac
        if frac == 1.0:
            req=" required"
        else:
            req=""
        if nonelectric and frac>0:
            scaledSupply = supply.integral*(1-frac) + (others.integral+demand.integral)*frac
        else:
            scaledSupply = supply.integral*(1-frac) + demand.integral*frac
        line.set_data(supply.time,y)
        if frac>0:
            text.set_text(f"{season} Supply{req}:\n{scaledSupply:.1f} GWd")
            text.set_y(y.max()* 0.7)
        fill.remove()
        del fill
        fill = ax.fill_between(
            supply.time, y, y2=0, alpha=scaled.opacity, color=scaled.color, hatch=scaled.hatch
        )

        ymin, ymax = ax.get_ylim()
        datamax = y.max()+10
        if datamax>=ymax:
            ax.set_ylim(0,datamax)
            ax.figure.canvas.draw()

        return line,


    #plt.tight_layout()
    #plt.show()
    Writer = animation.writers['ffmpeg']
    writer = Writer(fps=15, metadata=dict(artist='Me'), bitrate=1800)  # try -1 as well
    ani = animation.FuncAnimation(fig, run, scaleFactor, interval=50, repeat=False,
            cache_frame_data=False, blit=False)#, init_func=init)
    #plt.show()
    #ani.save('summer_scale.mp4', writer=writer)
    l2 = "sectors" if nonelectric else ""
    ani.save(f'{season}{l2}_scaleup.mp4', )
    #plt.savefig("solar-intermittency-scene1.png")



def add_axes(ax):
    # ax.legend(loc="upper left")
    ax.set_ylabel("Power (GW)")
    ax.set_xlabel("Time (hour of day)")
    ax.grid(alpha=0.3, ls="--")
    ax.set_ylim(bottom=0)
    ax.set_xlim([0, 24])
    ax.set_ylim([0, 120])
    ax.set_xticks(np.arange(0, 25, 3.0))

def plot_frames_alone():
    """I'm struggling with the animations a bit so maybe I can just do each frame
    individually."""


if __name__ == "__main__":
    data = read_data()
    # plot_demand(data)
    # plot_solar_supply(data)
    # plot_solar_scenario(data)
    #plot_summer_scenario(data)
    #scene1_summer("Winter", data)
    #scene1_summer("Summer", data)
    #scene1_summer("Winter", data, showSupply=False)
    #scene1_summer("Summer", data, showSupply=False)
    #scene2_scaleup("Summer", data)
    scene2_scaleup("Winter", data)
    scene2_scaleup("Winter", data, nonelectric=True)
