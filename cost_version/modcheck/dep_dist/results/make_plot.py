# This script generates a plot for invarient distribution comparison

import pandas as pd
import matplotlib.pyplot as plt

pdat = pd.read_csv('plot_csv.csv')
pdat = pdat[pdat['dep'] != 'OTHER']
pdat = pdat.set_index('dep')
pdat_scat = pdat[['dat','sim']]
pdat_scat.columns = ['data', 'simulation']

fig1 = plt.figure(figsize=(11,7))

plt.subplot(2,2,1)
plt.hist(pdat_scat['data'])
plt.xlabel('department size')
plt.ylabel('data')

plt.subplot(2,2,2)
plt.hist(pdat_scat['simulation'])
plt.xlabel('department size')
plt.ylabel('simulation mean')

plt.subplot(2,2,3)
plt.scatter(pdat_scat['data'],pdat_scat['simulation'])
plt.xlabel('data')
plt.ylabel('simulation means')

ax = plt.subplot(2,2,4)
plt.plot(pdat['dat'], 'or', linewidth=0.5)
plt.plot(pdat['ub'], '-b', linewidth=1)
plt.plot(pdat['lb'], '-b', linewidth=1)
plt.ylim([0,150])
plt.ylabel('department size')
ax.xaxis.set_major_formatter( plt.NullFormatter() )

plt.savefig('mov_plts.png')
plt.show()


