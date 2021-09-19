from matplotlib import pyplot as plt
import matplotlib
import numpy as np
from matplotlib_venn import venn3, venn3_circles

matplotlib.rcParams.update({"font.size": 16})

plt.figure(figsize=(12, 10))
v = venn3(
    subsets=(1, 1, 1, 1, 1, 1, 1),
    set_labels=("RENEWABLE", "SCALABLE NOW", "LOW CARBON"),
)
v.get_patch_by_id("100").set_alpha(1.0)
v.get_patch_by_id("010").set_color("#ebc6faff")
v.get_patch_by_id("001").set_color("#93ffb4ff")
v.get_patch_by_id("100").set_color("#cff0ffff")
v.get_label_by_id("100").set_text("Whale oil")
v.get_label_by_id("111").set_text("Wind,\nHydro,\nSolar")
v.get_label_by_id("111").set_weight("bold")
v.get_label_by_id("110").set_text("Biofuel\n(wood, corn)")
v.get_label_by_id("010").set_text("Coal,\nNatural gas,\nOil")
v.get_label_by_id("001").set_text("Fusion")
v.get_label_by_id("011").set_text("Fission")
v.get_label_by_id("011").set_weight("bold")
v.get_label_by_id("101").set_text("Geothermal,\nTidal")
# lv.get_label_by_id('RENEWABLE').set_size(24)
for label in ["A", "B", "C"]:
    l = v.get_label_by_id(label)
    l.set_size(24)
    l.set_weight("bold")
c = venn3_circles(subsets=(1, 1, 1, 1, 1, 1, 1), linestyle="solid", lw=0.5)
# c[0].set_lw(1.0)
# c[0].set_ls('dotted')
plt.annotate(
    "Could be farmed?\n(gross)",
    xy=v.get_label_by_id("100").get_position() - np.array([0, 0.03]),
    xytext=(-20, -50),
    ha="center",
    textcoords="offset points",
    size=10,
    bbox=dict(boxstyle="round,pad=0.5", fc="gray", alpha=0.1),
    arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0.5", color="gray"),
)
plt.annotate(
    "Not ready yet",
    xy=v.get_label_by_id("001").get_position() - np.array([0.07, 0.00]),
    xytext=(-50, 20),
    ha="center",
    textcoords="offset points",
    size=10,
    bbox=dict(boxstyle="round,pad=0.5", fc="gray", alpha=0.1),
    arrowprops=dict(arrowstyle="->", color="gray"),
)
#plt.show()
plt.savefig("renewable-venn.png")
