"""
Planet solar insolence graph.
"""
import numpy as np
import matplotlib.pyplot as plt

names = ['Mercury', 'Venus','Earth','Mars','Jupiter','Saturn','Uranus','Neptune','Pluto']
distances = [0.4,0.7,1.0,1.5,5.2,9.5, 19.2, 30.1, 39.0]
radiiKm = np.array([2440, 6052, 6378,3397, 71492, 60268,25559, 24766, 1150])
colors = ['gray','xkcd:pale yellow','xkcd:sky blue','xkcd:reddish brown','orange','xkcd:pale gold','xkcd:pale blue','xkcd:pale blue','xkcd:light brown']

insolence = 1/(np.array(distances)**2)
plt.figure()

plt.plot(distances, insolence, '--',color='k',alpha=0.7)
plt.scatter(distances, insolence, marker='o', c=colors, s = radiiKm/100)
ax = plt.gca()
for planet, color, radius, x,y in zip(names, colors, radiiKm, distances, insolence):
    ax.annotate(planet, xy=(x,y), textcoords='offset points',xytext=(20,3),arrowprops=dict(arrowstyle='->'))

#saturnRing = plt.Circle((distances[5],insolence[5]),5,color=colors[5])
#ax.add_artist(saturnRing)
plt.text(1,1e-3, 'whatisnuclear.com')
plt.title('How bright the Sun is from different planets')
plt.xlabel('Distance from Sun (AU)')
plt.ylabel('Relative solar insolence')
plt.grid(color='0.7',alpha=0.5,linestyle='--')

ax.set_yscale('log')
plt.tight_layout()
plt.subplots_adjust(right=0.9) 
plt.savefig('solar-system-insolence.png')


