from collections import OrderedDict
import os

import yaml
import matplotlib.pyplot as plt


def load(fname=os.path.join('..','data','energy-sources.yaml')):
    with open(fname) as f:
        alldata = yaml.load(f)
        data = alldata['co2 emissions']
    return data

def plot(data, fname='world-co2-emissions.png'):
    fig, ax = plt.subplots(figsize=(9,7))
    vals = data['val']
    x = range(2008,2019)
    for location, co2 in vals.items():
        co2 = [di/1e3 for di in co2] # convert to billion
        plt.plot(x, co2, '-o', label=location)
    plt.text(0.6,-0.1, 'Data from: {}'.format(data['ref']), transform=ax.transAxes,fontsize='x-small')
    plt.title(data['title'])
    plt.xlabel(data['xlabel'])
    plt.ylabel("Billion tonnes CO$_2$")
    plt.legend(loc='upper left')
    #plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
    #       ncol=2, mode="expand", borderaxespad=0.)
    if fname:
        plt.savefig(fname,dpi=300)
    else:
        plt.show()

if __name__ == '__main__':
    data = load()
    plot(data)
