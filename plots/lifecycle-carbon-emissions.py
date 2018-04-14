"""Plot capacity factors."""

import os
from operator import itemgetter

import yaml
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm


def load(fname=os.path.join('..','data','energy-sources.yaml')):
    with open(fname) as f:
        alldata = yaml.load(f)
        data = alldata['lifecycle emissions']
    return data

def plot(data, fname='lifecycle-carbon-emissions.png'):
    labels, values = zip(*reversed(sorted(data['val'].items(), 
                                          key=lambda (key, val): val[1])))
    labels = [label.capitalize() for label in labels]
    values = np.array(values)[:,1]
    width = 0.35
    index = np.arange(len(labels))

    fig, ax = plt.subplots()
    #colors = cm.YlGn_r(values/100.0)
    #bars = ax.bar(index, values, width, color=colors)
    bars = ax.bar(index, values, width)

    plt.title(data['title'])
    ax.set_ylabel('Lifecycle emissions ({})'.format(data['units']))
    ax.set_xticks(index)
    ax.set_xticklabels(labels)
    ax.grid(color='0.7', linestyle='--', axis='y')
    plt.xticks(rotation=90)
    plt.tight_layout()

    if fname:
        plt.savefig(fname)
    else:
        plt.show()

if __name__ == '__main__':
    data = load()
    plot(data)
