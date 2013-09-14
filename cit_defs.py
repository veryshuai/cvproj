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

def cit_lik_no_cit(alp, bet, gam, dep_aut, dep_year, lat):
    # calculates a single no cit authors lik

    lin1 = dep_aut.iloc[0]
    palp = alp[lin1['qual']][lin1['isField']][lat]
    pgam = gam[lin1['qual']][lin1['isField']][lat]
    liks = dep_aut.apply(lambda row: no_cit_inner(row, palp,
                                                   bet, dep_year), axis=1)
    arg = (1 - pgam + pgam * liks.prod())
    return arg

def cit_lik_cit(alp, bet, gam, dep_aut, dep_year, lat):
    # calculates a single cit authors lik

    lin1 = dep_aut.iloc[0]
    palp = alp[lin1['qual']][lin1['isField']][lat]
    pgam = gam[lin1['qual']][lin1['isField']][lat]
    liks = dep_aut.apply(lambda row: no_cit_inner(row, palp,
                                                   bet, dep_year), axis=1)
    arg = (pgam * liks.prod())
    return arg

def fc_lik(alp, bet, gam, dep_aut, dep_year, lat):
    # calculates first cite likelihoods

    lin1 = dep_aut.iloc[0]
    palp = alp[lin1['qual']][lin1['isField']][lat]
    pgam = gam[lin1['qual']][lin1['isField']][lat]
    liks = dep_aut.apply(lambda row: cit_inner(row, palp,
                                                   bet, dep_year), axis=1)
    arg = (pgam * liks.prod())
    return arg

def trans_prob(row, t):
    # retrieves correct value from transition prob matrix
    return t.ix[row['last_dep']][row['dep']]

def mov_lik(trans, group, lat): 
    # calculates movement likelihood
    # BUILT IN ASSUMPTION: IF YOU START AND END AT SAME
    # DEPARTMENT, YOU NEVER MOVED!

    lin1 = group.iloc[0]
    if lat == 1 and lin1['isField'] == 0:
        return 1
    else:
        lin2 = group.iloc[-1]
        t = trans[lin1['qual']][lin1['isField']][lat]
        if lin1['dep'] == lin2['dep']:
            out = trans_prob(lin1, t) * group.shape[0]
            return float(out)
        else:
            lik = group.apply(lambda row: trans_prob(row, t), axis=1)
            return lik.prod()


# aut_pan = pd.read_pickle('initial_panel.pickle')
# dep_year = pd.read_pickle('dep_years.pickle')
# first_cits = pd.read_pickle('first_cits.pickle')
# citers = pd.read_pickle('citers.pickle')
# nocits = pd.read_pickle('nocits.pickle')
# mov_dat = pd.read_pickle('mov_dat.pickle')
# f = file('trans.pickle','rb')
# trans = pickle.load(f)
# 
# # MOVE LIKS
# tik = clock()
# mlik = []
# for lat in range(2):
#     mlik.append(mov_dat.groupby('au').apply(lambda x: mov_lik(trans, x, lat)))
# tok = clock() - tik
# print tok
# 
# alp = tree()
# gam = tree()
# for qual in range(3):
#     for field in range(2):
#         for lat in range(2):
#             alp[qual][field][lat] = 0.1
#             gam[qual][field][lat] = 0.1
# 
# tot = 0
# tik = clock()
# cit_liks, fc_liks, nocit_liks = [], [], []
# for lat in range(2):
#     cit_liks.append(citers.groupby('au')\
#                 .apply(lambda x: cit_lik_cit(alp, 100, gam, 0.1, x, dep_year, lat)))
#     fc_liks.append(first_cits.groupby('au')\
#                 .apply(lambda x: fc_lik(alp, 100, gam, 0.1,  x, dep_year, lat)))
#     nocit_liks.append(nocits.groupby('au')\
#                 .apply(lambda x: cit_lik_no_cit(alp, 100, gam, 0, x, dep_year, lat)))
# 
# #tot += cit_liks.sum() + fc_liks.sum() + nocit_liks.sum()
# print tot
# tok = clock() - tik
# print tok


