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

def no_cit_inner(row, alp, bet, dep_year, lat, qp):
    k_lev = dep_year.at[row['dep'],row['date']-1]
    num = alp[0] + alp[1] * row['date']\
            + bet * k_lev + qp[lat]
    item = 1 - math.exp(num) / (1 + math.exp(num))
    return item

def cit_lik_no_cit(alp, bet, gam, dep_aut,
                   dep_year, lat, qp):
    # calculates a single no cit authors lik

    lin1 = dep_aut.iloc[0]
    pgam = gam[lin1['isField']]
    liks = dep_aut.apply(lambda row: no_cit_inner(row, alp,
                                                   bet, dep_year,
                                                   lat, qp), axis=1)
    arg = (1 - pgam + pgam * liks.prod())
    return arg

def cit_lik_cit(alp, bet, gam, dep_aut,
                dep_year, lat, qp):
    # calculates a single cit authors lik

    lin1 = dep_aut.iloc[0]
    pgam = gam[lin1['isField']]
    liks = dep_aut.apply(lambda row: no_cit_inner(row, alp,
                                               bet, dep_year,
                                               lat, qp), axis=1)
    arg = (pgam * liks.prod())
    return arg

def fc_lik(alp, bet, gam, dep_aut,
           dep_year, lat, qp):
    # calculates first cite likelihoods

    lin1 = dep_aut.iloc[-1]
    pgam = gam[lin1['isField']]
    num = alp[0] + alp[1] * lin1['date'] + qp[lat]\
            + bet * dep_year.at[lin1['dep'],lin1['date']-1]
    item = math.exp(num) / (1 + math.exp(num))
    return item

def trans_prob(row, t):
    # retrieves correct value from transition prob matrix
    return t.loc[row['last_dep']][row['dep']]

def mov_lik(trans, group, lat): 
    # calculates movement likelihood
    # BUILT IN ASSUMPTION: IF YOU START AND END AT SAME
    # DEPARTMENT, YOU NEVER MOVED!

    lin1 = group.iloc[0]
    t = trans[lin1['qual']][lin1['isField']][lat]
    if not t:
        return 0
    else:
        lin2 = group.iloc[-1]
        if lin1['last_dep'] == lin2['dep']:
            out = pow(trans_prob(lin1, t),group.shape[0])
            return max(float(out), 1e-12) #avoit zeros
        else:
            lik = group.apply(lambda row: trans_prob(row, t), axis=1)
            return max(lik.prod(), 1e-12)  #avoid zeros
