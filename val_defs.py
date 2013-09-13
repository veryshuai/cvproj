# This file contains definition for value function iteration in the discrete version of my model.

import pandas as pd
import numpy as np

def val_init(mov_params, dep_stats, lam, dis, p):
    # initializes value function iteration

    for qual in range(3):
        for field in range(2):
            for lat in range(2):
                wage = calc_wage(mov_params, dep_stats, qual, field, lat)
                vals = val_loop(wage, lam, dis, p)
    return 0

def mins(v, dat, p):
    # Returns the min operation used in val fun iteration
    out = dat.apply(lambda x: min(pow(x[1]/(v[0] + v[1] - x[0]),p), 1), axis = 1)
    return out

def maxs(v, dat, p):
    # Returns the max operation used in val fun iteration
    out = dat.apply(lambda x: max(x[1], v[1] + v[0] - x[0]), axis = 1)
    return out

def ft(dat):
    # Returns the first term used in val fun iteration
    out = dat.apply(lambda x: dat['v1'], axis = 1)
    return out

def calc_exp(currents, w, p):
    # caculates expectation part of value function

    dat = pd.DataFrame({'v1': currents, 'w1': w})
    min_stat = dat.apply(lambda row: mins(row, dat, p), axis=1)
    max_stat = dat.apply(lambda row: maxs(row, dat, p), axis=1)
    exp_mat = currents.transpose() + max_stat * (1 + 1 / (float(p) - 1) * min_stat)
    exp_mat = exp_mat.as_matrix()
    np.fill_diagonal(exp_mat,0)
    exp = pd.Series(exp_mat.sum(0), index=currents.index)
    exp = exp / (len(currents)-1)
    return exp

def val_eval(currents, w, lam, dis, p):
    # This function evaluates the value function

    # EXPECTATION 
    exp = calc_exp(currents, w, p)

    # REST
    new = dis * (1 - lam) / (1 - dis * (1 - lam)) * w\
            + dis * lam / (1 - dis * (1 - lam)) * exp
    return new

def val_loop(w, lam, dis, p):
    # This function begins the value function loop

    # INITIAL GUESS
    current = w.apply(lambda x: x.max() / (1 - dis))

    dif = 1
    while dif > 1e-3:
        new = val_eval(current, w, lam, dis,p)
        print new

        dif = pow(new - current,2)
        dif = dif.sum()
        print dif
        current = new.copy()
    return new

def wd(ind, dep):
    # peforms distance calculation for wage

    out = dep.apply(lambda x: 1 / (1 + pow(ind - x,2)))
    return out


def calc_wage(mp, dep, qual, field, lat):
    # returns wage at each of the departments

    # EASY PARAMETER REFERENCE
    q = mp['qual']
    f = mp['field']
    l = mp['lat']

    # CALCULATE WAGE
    wq = q * wd(qual, dep['dep_qual'])
    wf = f * wd(field, dep['dmean'])
    wl = l * wd(lat, dep['dmean'])
    w = wq + wf + wl

    return w

mov_params = pd.Series({'qual': 1, 'field': 1, 'lat': 1})
dep_stats = pd.read_pickle('dep_list.pickle').set_index('dep')
val_init(mov_params, dep_stats, 0.05, 0.95, 10000)
