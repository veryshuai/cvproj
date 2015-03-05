# This script compares the long-run distribution of academics over departments in the data to the model.

import pandas as pd
import matplotlib.pyplot as plt

sim = pd.read_csv('spb.csv')
dat = pd.read_csv('dep_dat.csv')
merged = pd.merge(sim,dat,on='dep')
print merged
merged['npop'] = merged['pop_x'] / float(merged['pop_x'].sum())
merged['ndep'] = merged['pop_y'] / float(merged['pop_y'].sum())
merged.to_csv('test.csv')

npop = sim['pop'] / float(sim['pop'].sum())
ndep = dat['pop'] / float(dat['pop'].sum())
cov =  npop.cov(ndep)
sd1 = npop.describe()['std']
sd2 = npop.describe()['std']
print cov / (sd1 * sd2)

joined = pd.DataFrame({'sim':npop,'dat':ndep})
joined.hist()
plt.show()

