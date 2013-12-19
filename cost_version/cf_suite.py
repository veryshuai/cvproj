# This file contains definitions for functions related to running counterfactuals

import val_defs as vd
import random
from scipy.stats import norm
import collections
import pandas as pd
from copy import copy, deepcopy

#From stefan at stack overflow:
#http://stackoverflow.com/questions/3009935/looking-for-a-good-python-tree-data-structure
def tree():
    return collections.defaultdict(tree)

def make_lat(dmean, lp): 
    """ stochastically assigns latent type """
    if random.random() < norm.cdf(lp[0] + lp[1] * dmean):
        return 1
    else:
        return 0

def make_moves(r, trans):
    dep_list = [r['dep'].iat[0]]
    year_list = [r['date'].iat[0]]
    t = trans[r['qual'].iat[0]][r['isField'].iat[0]][r['isLatent'].iat[0]]
    while year_list[-1] < 1994:
        tr = t.loc[dep_list[-1]].transpose().cumsum().reset_index()
        rnd = random.random()
        tr['truth'] = tr[0] > rnd
        try:
            next_dep = tr['index'][tr['truth']].iat[0]
        except:
            next_dep = tr['dep'][tr['truth']].iat[0]
        dep_list.append(next_dep)
        year_list.append(year_list[-1] + 1)
    return pd.DataFrame({'dep': dep_list, 'yr': year_list, 'qual': qual, 'isLatent': isLatent, 'isField': isField})

def offer_cf(lo_cf, cit_params, big_mov_params,
             lp, init, ip, dep_stats, bd, aut_pan):
    # Simulates the evolution of knowledge
    # spread with different offer frequency

    # INSERT COUNTERFACTUAL OFFER PROBABILITY
    big_mov_params = [big_mov_params[0], lo_cf, big_mov_params[2]]
    init, trans, itrans = vd.val_init(big_mov_params, dep_stats,
                                      0.9, ip, bd, init)

    # ASSIGN LATENT TYPES TO 1987 AUTHORS
    aut_pan = aut_pan[aut_pan['date'] == 1987]
    aut_pan['isLatent'] = aut_pan['dmean']\
            .apply(lambda x: make_lat(x, lp))

    # SIMULATE MOVES BETWEEN DEPARTMENTS
    moves = aut_pan.groupby('au').apply(lambda x:
                                          make_moves(x, trans))

    # SIMULATE SPREAD OF KNOWLEDGE THROUGH DEPARTMENTS

    import pdb; pdb.set_trace()

def run_cf():
    """ reads from a results file, and calls
        counterfactual generation program """
    lo_cf = 0.1




