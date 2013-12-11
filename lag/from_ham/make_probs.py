# This script generates learning probabilities for field and not field

import pandas as pd
import math
import matplotlib.pyplot as plt

#READ IN DATA
dat = pd.read_csv('out.csv')

def gen_probs(row, kfrac, field):
    num = math.exp(row['alp'] + row[' bet'] * kfrac + field)
    return num / (1 + num)

lf0   = dat.apply(lambda row: gen_probs(row, 0.0, -2), axis=1)
lf10  = dat.apply(lambda row: gen_probs(row, 0.05, -2), axis=1)
mf0      = dat.apply(lambda row: gen_probs(row, 0.0, -1), axis=1)
mf10     = dat.apply(lambda row: gen_probs(row, 0.05, -1), axis=1)
hf0      = dat.apply(lambda row: gen_probs(row, 0.0, 0), axis=1)
hf10     = dat.apply(lambda row: gen_probs(row, 0.05, 0), axis=1)
learn_probs = pd.DataFrame({ 'low lat 0%': lf0, 'mid lat 0%': mf0, 'high lat 0%': hf0, 'low lat 5%': lf10, 'mid lat 5%': mf10, 'high lat 5%': hf10})
learn_probs = learn_probs[['low lat 0%', 'mid lat 0%', 'high lat 0%', 'low lat 5%', 'mid lat 5%', 'high lat 5%']]

print learn_probs

fig, axes = plt.subplots(nrows=2, ncols=3)
learn_probs['low lat 0%'].hist(bins=25, ax=axes[0,0], figsize=(17,8)); axes[0,0].set_title('low lat 0%'); axes[0,0].set_xlim([0,1])
learn_probs['mid lat 0%'].hist(bins=25, ax=axes[0,1], figsize=(17,8)); axes[0,1].set_title('mid lat 0%'); axes[0,1].set_xlim([0,1])
learn_probs['high lat 0%'].hist(bins=25, ax=axes[0,2], figsize=(17,8)); axes[0,2].set_title('high lat 0%'); axes[0,2].set_xlim([0,1])
learn_probs['low lat 5%'].hist(bins=25, ax=axes[1,0], figsize=(17,8)); axes[1,0].set_title('low lat 5%'); axes[1,0].set_xlim([0,1])
learn_probs['mid lat 5%'].hist(bins=25, ax=axes[1,1], figsize=(17,8)); axes[1,1].set_title('mid lat 5%'); axes[1,1].set_xlim([0,1])
learn_probs['high lat 5%'].hist(bins=25, ax=axes[1,2], figsize=(17,8)); axes[1,2].set_title('high lat 5%'); axes[1,2].set_xlim([0,1])
fig.tight_layout()

plt.savefig('learn_probs.png', bbox_inches=0)
plt.show()


