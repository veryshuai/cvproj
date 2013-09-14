# This script contains functions for calculating the
# citation hazards in the discrete version of my model

import pandas as pd
import math
from time import clock, time
import collections
import random
import pickle

#From stefan at stack overflow:
#http://stackoverflow.com/questions/3009935/looking-for-a-good-python-tree-data-structure
def tree():
    return collections.defaultdict(tree)

def no_cit_inner(row, alp, bet, dep_year):
    k_lev = dep_year.at[row['dep'],row['date']-1]
    num = alp + bet * k_lev
    item = 1 - num / (1 + num)
    return item

def cit_inner(row, alp, bet, dep_year):
    num = alp + bet * dep_year.at[row['dep'],row['date']-1]
    item = 1 - num / (1 + num)
    return item

def cit_lik_no_cit(alp, bet, gam, lp, dep_aut, dep_year):
    # calculates a single no cit authors lik

    lin1 = dep_aut.iloc[0]
    palp = alp[lin1['qual']][lin1['isField']]
    pgam = gam[lin1['qual']][lin1['isField']]
    liks = []
    liks.append(dep_aut.apply(lambda row: no_cit_inner(row, palp[0],
                                                   bet, dep_year), axis=1))
    # check for latent type possibility
    if lp != 0:
        liks.append(dep_aut.apply(lambda row: no_cit_inner(row, palp[1],
                                                   bet, dep_year), axis=1))
        arg0 = (1 - pgam[0] + pgam[0] * liks[0].prod())
        arg1 = (1 - pgam[1] + pgam[1] * liks[1].prod())
        return math.log(lp * arg0 + (1 - lp) * arg1)
    else:
        arg0 = (1 - pgam[0] + pgam[0] * liks[0].prod())
        return math.log(arg0)

def cit_lik_cit(alp, bet, gam, lp, dep_aut, dep_year):
    # calculates a single cit authors lik

    lin1 = dep_aut.iloc[0]
    palp = alp[lin1['qual']][lin1['isField']]
    pgam = gam[lin1['qual']][lin1['isField']]
    liks = []
    liks.append(dep_aut.apply(lambda row: no_cit_inner(row, palp[0],
                                                   bet, dep_year), axis=1))
    liks.append(dep_aut.apply(lambda row: no_cit_inner(row, palp[1],
                                                   bet, dep_year), axis=1))
    arg0 = (pgam[0] * liks[0].prod())
    arg1 = (pgam[1] * liks[1].prod())
    return math.log(lp * arg0 + (1 - lp) * arg1)

def fc_lik(alp, bet, gam, lp, dep_aut, dep_year):
    # calculates first cite likelihoods

    lin1 = dep_aut.iloc[0]
    palp = alp[lin1['qual']][lin1['isField']]
    pgam = gam[lin1['qual']][lin1['isField']]
    liks = []
    liks.append(dep_aut.apply(lambda row: cit_inner(row, palp[0],
                                                   bet, dep_year), axis=1))
    liks.append(dep_aut.apply(lambda row: cit_inner(row, palp[1],
                                                   bet, dep_year), axis=1))
    arg0 = (pgam[0] * liks[0].prod())
    arg1 = (pgam[1] * liks[1].prod())
    return math.log(lp * arg0 + (1 - lp) * arg1)

dep_year = pd.read_pickle('dep_years.pickle')
first_cits = pd.read_pickle('first_cits.pickle')
citers = pd.read_pickle('citers.pickle')
nocits = pd.read_pickle('nocits.pickle')
f = file('trans.pickle','rb')
trans = pickle.load(f)
print trans[0][0][0]

alp = tree()
gam = tree()
for qual in range(3):
    for field in range(2):
        for lat in range(2):
            alp[qual][field][lat] = 0.1
            gam[qual][field][lat] = 0.1

tot = 0
tik = clock()
cit_liks = citers.groupby('au')\
            .apply(lambda x: cit_lik_cit(alp, 100, gam, 0.1, x, dep_year))
fc_liks = first_cits.groupby('au')\
            .apply(lambda x: fc_lik(alp, 100, gam, 0.1,  x, dep_year))
nocit_liks = nocits.groupby('au')\
            .apply(lambda x: cit_lik_no_cit(alp, 100, gam, 0, x, dep_year))

tot += cit_liks.sum() + fc_liks.sum() + nocit_liks.sum()
print tot
tok = clock() - tik
print tok


