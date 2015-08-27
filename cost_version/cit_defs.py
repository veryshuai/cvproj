# This script contains functions for calculating the
# citation hazards in the discrete version of my model

import pandas as pd
import math
from time import clock, time
import collections
import random
import pickle
import numpy as np

#From stefan at stack overflow:
#http://stackoverflow.com/questions/3009935/looking-for-a-good-python-tree-data-structure
def tree():
    return collections.defaultdict(tree)

def no_cit_inner(row, alp, bet, gam, lat, qp):

    dur = row['duration']
    k_lev = row['lag_total_exp']
    adj_yr = row['date']-1987
    num = alp[0]\
            + bet[0] * k_lev\
            + gam[0] * row['isField']\
            + alp[1] * adj_yr\
            + alp[2] * adj_yr ** 2\
            + alp[3] * dur\
            + alp[4] * dur ** 2\
            + qp[row['high_field_first_dep']][lat]
    try:
        item = math.exp(-num) / (1 + math.exp(-num))
    except Exception as e:
        print 'WARNING: overflow error, assigned small lik' 
        item = 1e-20
    return item

def cit_lik_no_cit(alp, bet, gam, dep_aut,
                    lat, qp):
    # calculates a single no cit authors lik

    lin1 = dep_aut.iloc[0]
    #pgam = gam[lin1['isField']]
    liks = dep_aut.apply(lambda row: no_cit_inner(row, alp,
                                                   bet, gam,
                                                   lat, qp), axis=1)
    #arg = (1 - pgam + pgam * liks.prod())
    arg = liks.prod()
    return arg

def cit_lik_cit(alp, bet, gam, dep_aut,
                 lat, qp):
    # calculates a single cit authors lik

    lin1 = dep_aut.iloc[0]
    #pgam = gam[lin1['isField']]
    liks = dep_aut.apply(lambda row: no_cit_inner(row, alp,
                                               bet, gam,
                                               lat, qp), axis=1)
    #arg = (pgam * liks.prod())
    arg = liks.prod()
    return arg

def fc_lik(alp, bet, gam, dep_aut,
            lat, qp):
    # calculates first cite likelihoods
    lin1 = dep_aut.iloc[-1]
    #pgam = gam[lin1['isField']]

    dur = dep_aut['duration']
    k_lev = dep_aut['lag_total_exp']
    adj_yr = dep_aut['date']-1987
    num = alp[0]\
            + bet[0] * k_lev\
            + gam[0] * lin1['isField']\
            + alp[1] * adj_yr\
            + alp[2] * adj_yr ** 2\
            + alp[3] * dur\
            + alp[4] * dur ** 2\
            + qp[lin1['high_field_first_dep']][lat]
    item = 1 / (1 + math.exp(-num))
    return item

def trans_prob(row, t):
    # retrieves correct value from transition prob matrix
    return t.loc[row['last_dep']][row['dep']]

def mov_lik(trans, group, lat): 
    # calculates movement likelihood
    # BUILT IN ASSUMPTION: IF YOU START AND END AT SAME
    # DEPARTMENT, YOU NEVER MOVED!

    lin1 = group.iloc[0]
    t = trans[lin1['qual']][lin1['isField']][lat][lin1['high_field_first_dep']]
    # if not t: #I'm not sure what this check was for...
    #     return 0
    # else:
    lin2 = group.iloc[-1]
    if lin1['last_dep'] == lin2['dep']:
        out = pow(trans_prob(lin1, t),group.shape[0])
        return max(float(out), 1e-12) #avoid zeros
    else:
        lik = group.apply(lambda row: trans_prob(row, t), axis=1)
        return max(lik.prod(), 1e-12)  #avoid zeros
