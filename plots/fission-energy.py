
import matplotlib.pyplot as plt
import numpy as np

labels = []
energy = []
with open('../data/u235-endf71-fission-energy.csv') as f:
    for line in f:
        data = line.split(',')
        labels.append(data[0])
        energy.append(float(data[1])/1e6)

total = sum(energy)
# 950 MWd/kg max U235
energy = [e/total*950 for e in energy]

fig, ax = plt.subplots(dpi=150, figsize=(8,5))
width= 0.35
index = np.arange(len(labels))
bars = ax.bar(index, energy, width)
ax.set_ylim([0,900]) # make room for data label
ax.set_xticks(index)
ax.set_xticklabels(labels)
ax.tick_params(axis = 'x', which = 'major', labelsize = 10)

ax.axvline(x=2.5, color='k', ls="--")
ax.axvline(x=5.5, color='k', ls="--")

# data labels
for bar in bars:
    height = bar.get_height()
    if height<1:
        val = f"{height:.3f}"
    else:
        val = f"{height:.0f}"
    ax.annotate(val,
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3),  # 3 points vertical offset
                textcoords="offset points",
                ha='center', va='bottom', size=6)


ax.set_ylabel("Energy released (megawatt days)")
#ax.set_xlabel("Radiation type")
plt.title("Energy release from fission of 1 kg $^{235}$Uranium")
plt.xticks(rotation=50, ha="right")
props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
props2 = dict(boxstyle='round', facecolor='skyblue', alpha=0.5)
ax.text(1.30,600,"These come\nimmediately after\nfission and\nstop after\nreactor shutdown", 
        va='center', ha='center', bbox=props, fontsize="10")

ax.text(4,600,
        "These come between\nmilliseconds and millenia\nafter fission and continue\n"
        "after reactor shutdown", 
        va='center', ha='center', bbox=props, fontsize="10")

ax.text(4,200,
        "This afterglow heat\nis why nuclear\nwaste is hazardous",
        va='center', ha='center', fontweight='bold',bbox=props2, fontsize="10")

ax.text(6,600,
        "These\nrarely\ninteract\nwith\nanything!",
        va='center', ha='center', bbox=props, fontsize="10")

fig.subplots_adjust(bottom=0.25, top=0.95)
plt.savefig('fission-energy.svg')
#plt.show()
