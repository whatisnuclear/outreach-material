"""Plot capacity factors."""

import os

import yaml
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm


def load(fname=os.path.join('..','data','energy-sources.yaml')):
    with open(fname) as f:
        alldata = yaml.load(f)
        data = alldata['capacity factors in usa']
    return data

def plot(data, fname='capacity-factors-usa.png'):
    labels, values = zip(*sorted(data['val'].items()))
    labels = [label.capitalize() for label in labels]
    values = np.array(values)
    width = 0.35
    index = np.arange(len(labels))

    fig, ax = plt.subplots()
    colors = cm.YlGn(values/100.0)
    bars = ax.bar(index, values, width, color=colors)

    plt.title(data['title'])
    ax.set_ylabel('Capacity factor (%)')
    ax.set_xticks(index)
    ax.set_xticklabels(labels)
    ax.set_yticks(np.arange(0,101,10))
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
