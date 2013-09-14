# This script contains functions for calculating the
# citation hazards in the discrete version of my model

import pandas as pd
import math
from time import clock, time
import collections
import random

#From stefan at stack overflow:
#http://stackoverflow.com/questions/3009935/looking-for-a-good-python-tree-data-structure
def tree():
    return collections.defaultdict(tree)

def no_cit_inner(row, alp, bet, dep_year):
    print row
    k_lev = dep_year.at[row['dep'],row['date']-1]
    num0 = alp[0] + bet * k_lev
    item0 = 1 - num0 / (1 + num0)
    num1 = alp[1] + bet * k_lev
    item1 = 1 - num1 / (1 + num1)
    return item0, item1

def cit_inner(row, alp, bet, dep_year):
    num = alp + bet * dep_year.at[row['dep'],row['date']-1]
    item = 1 - num / (1 + num)
    return item

def cit_lik_no_cit(alp, bet, gam, lp, dep_aut, dep_year):
    # calculates a single no cit authors lik

    lin1 = dep_aut.iloc[0]
    palp = alp[lin1['qual']][lin1['isField']]
    pgam = gam[lin1['qual']][lin1['isField']]
    liks =  dep_aut.apply(lambda row: no_cit_inner(row, palp,
                                                   bet, dep_year), axis=1)

    arg0 = (1 - pgam[0] + pgam[0] * liks[0].prod())
    arg1 = (1 - pgam[1] + pgam[1] * liks[1].prod())
    return math.log(lp * arg0 + (1 - lp) * arg1)

def cit_lik_cit(alp, bet, gam, lp, dep_aut, dep_year):
    # calculates a single cit authors lik

    lin1 = dep_aut.iloc[0]
    palp = alp[lin1['qual']][lin1['isField']]
    pgam = gam[lin1['qual']][lin1['isField']]
    liks =  dep_aut.apply(lambda row: no_cit_inner(row, palp,
                                                   bet, dep_year), axis=1)
    arg0 = (pgam[0] * liks[0].prod())
    arg1 = (pgam[1] * liks[1].prod())
    return math.log(lp * arg0 + (1 - lp) * arg1)

def fc_lik(alp, bet, gam, lp, dep_aut, dep_year):
    # calculates first cite likelihoods

    lin1 = dep_aut.iloc[0]
    palp = alp[lin1['qual']][lin1['isField']][0]
    pgam = gam[lin1['qual']][lin1['isField']][0]
    liks = dep_aut.apply(lambda row: cit_inner(row, palp,
                                                   bet, dep_year), axis=1)
    return (math.log(pgam * liks))

dep_year = pd.read_pickle('dep_years.pickle')
aut_pan = pd.read_pickle('initial_panel.pickle')
aut_pan = aut_pan[aut_pan['date'] > 1986]
first_cits = aut_pan[aut_pan['isCiter'] == 1].sort_index(by='date')\
             .groupby('au').first().reset_index()
print first_cits
aut_pan['ever_cit'] = aut_pan.groupby('au')['isCiter']\
        .transform(lambda x: max(x))
citers = aut_pan[aut_pan['ever_cit'] == 1]
nocits = aut_pan[aut_pan['ever_cit'] == 0]

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
            .apply(lambda x: cit_lik_no_cit(alp, 100, gam, 0.1, x, dep_year))

tot += cit_liks.sum() + fc_liks.sum() + nocit_liks.sum()
print tot
tok = clock() - tik
print tok


# tot = 0
# tik = clock()
# for qual in range(3):
#     for field in range(2):
#         cit_liks = citers[(citers['isField'] == field)
#                              & (citers['qual'] == qual)]\
#                             .groupby('au')\
#                             .apply(lambda x: cit_lik_cit(.1, 100, .1,
#                                                          x, dep_year))
#         fc_liks = first_cits[(first_cits['isField'] == field)
#                              & (first_cits['qual'] == qual)]\
#                             .groupby('au')\
#                             .apply(lambda x: fc_lik(.1, 100, .1,
#                                                          x, dep_year)) 
#         nocit_liks = nocits[(nocits['isField'] == field)
#                              & (nocits['qual'] == qual)]\
#                             .groupby('au')\
#                             .apply(lambda x: cit_lik_no_cit(.1, 100, .1,
#                                                          x, dep_year))
#         tot += cit_liks.sum() + fc_liks.sum() + nocit_liks.sum()
# print tot
# tok = clock() - tik
# print tok



