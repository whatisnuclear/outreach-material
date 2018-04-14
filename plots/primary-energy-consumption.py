from collections import OrderedDict
import os

import yaml
import matplotlib.pyplot as plt


def load(fname=os.path.join('..','data','energy-sources.yaml')):
    with open(fname) as f:
        alldata = yaml.load(f)
        data = alldata['worldwide consumption']
    return data

def plot(data, fname='primary-energy-consumption.png'):
    fig, ax = plt.subplots()
    # hardcode order to get colors right.
    labels = ['oil','natural gas','coal','nuclear','hydro','renewables']
    vals = [data['val'][lb] for lb in labels]
    labels = [lb.capitalize() for lb in labels]
    colors = ['0.5','0.6','0.7', 'greenyellow','limegreen','springgreen']
    ax.pie(vals, labels=labels, autopct='%1.0f%%',colors=colors)
    ax.axis('equal')
    plt.text(0.2,-0.1, 'Data from: {}'.format(data['ref']), transform=ax.transAxes,fontsize='x-small')
    plt.title(data['title'])
    if fname:
        plt.savefig(fname,dpi=300)
    else:
        plt.show()

if __name__ == '__main__':
    data = load()
    plot(data)
