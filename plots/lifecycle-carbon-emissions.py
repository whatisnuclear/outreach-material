"""Plot capacity factors."""

import os
from operator import itemgetter
import textwrap

import yaml
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm


def load(fname=os.path.join('..','data','energy-sources.yaml')):
    with open(fname) as f:
        alldata = yaml.load(f)
        data = alldata['lifecycle emissions']
    return data

def plot(data, fname='lifecycle-carbon-emissions-nolabel.png'):
    labels, values = zip(*reversed(sorted(data['val'].items(), 
                                          key=lambda kv: kv[1][1])))
    labels = [label.capitalize() for label in labels]
    values = np.array(values)[:,1]
    width = 0.35
    index = np.arange(len(labels))

    fig, ax = plt.subplots(dpi=300)
    # _r is for reversed colormap :)
    colors = cm.RdYlGn_r(values/100.0)
    bars = ax.bar(index, values, width, color=colors, edgecolor="k")
    #bars = ax.bar(index, values, width)

    plt.title(data['title'])
    ax.set_ylabel('Lifecycle emissions ({})'.format(data['units']))
    ax.set_xticks(index)
    ax.set_xticklabels(labels)
    ax.grid(alpha=0.7, linestyle='--', axis='y')
    # ha needed or else labels rotate on center
    plt.xticks(rotation=50, ha="right")
    ax.set_ylim([0,900]) # make room for data label

    # Add data labels on each bar
    for bar in bars:
        height = bar.get_height()
        ax.annotate('{:.0f}'.format(height),
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom', size=6)
    
    # Point out nuclear
    ann = ax.annotate("Nuclear is among\nthe lowest-carbon forms\nof energy we know",
                  xy=(11, 70), xycoords='data',
                  xytext=(8, 500), textcoords='data',
                  size=12, va="center", ha="center",
                  bbox=dict(boxstyle="round4", fc="w"),
                  arrowprops=dict(arrowstyle="-|>",
                                  connectionstyle="arc3,rad=-0.2",
                                  fc="w"),
                  )
    #plt.tight_layout()
    # Manually squish the subplot to make room for labels
    fig.subplots_adjust(bottom=0.4,top=0.90)
    ann = ax.text(0.1, 0.1, '\n'.join(textwrap.wrap(data['ref'] + ". Plot by whatisnuclear.com.",130)),
                  size=6, va="center", ha="left", transform=fig.transFigure
                  )


    if fname:
        plt.savefig(fname)
    else:
        plt.show()

if __name__ == '__main__':
    data = load()
    plot(data, 'lifecycle-carbon-emissions.pdf')
