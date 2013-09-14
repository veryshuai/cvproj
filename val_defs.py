# This file contains definition for value function
# iteration in the discrete version of my model.

import pandas as pd
import numpy as np
import collections
import cyfuncs as cyf
import pickle

#From stefan at stack overflow:
#http://stackoverflow.com/questions/3009935/looking-for-a-good-python-tree-data-structure
def tree():
    return collections.defaultdict(tree)

def val_init(mov_params, dep_stats, lam, dis, p, init=[]):
    # initializes value function iteration

    vals = tree()
    trans = tree();
    for qual in range(3):
        for field in range(2):
            for lat in range(2):
                wage = calc_wage(mov_params, dep_stats,
                                 qual, field, lat)
                try:
                    sp = init[qual][field][lat]
                    vals[qual][field][lat], trans[qual][field][lat]\
                        = val_loop(wage, lam, dis, p, sp)
                except Exception as e:
                    print 'WARNING: Value function start point error,\
                             file val_defs.py, function val_init'
                    print e
                    vals[qual][field][lat], trans[qual][field][lat]\
                        = val_loop(wage, lam, dis, p)
    return vals, trans

def mins(v, dat, p):
    # Returns the min operation used in val fun iteration
    out = dat.apply(lambda x: cyf.cminex(x[1], x[0], v[1], v[0], p), axis=1)
    return out

def maxs(v, dat, p):
    # Returns the max operation used in val fun iteration
    out = dat.apply(lambda x: cyf.cmaxex(x[1], x[0], v[1], v[0]), axis=1)
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
    exp_mat = currents.transpose() \
            + max_stat * (1 + 1 / (float(p) - 1) * min_stat)
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

def val_loop_inner(current, w, lam, dis, p):
    # runs actual val loop
    dif = 1
    iters = 0
    while dif > 1e-1 and iters < 20:
        new = val_eval(current, w, lam, dis, p)
        dif = pow(new - current,2)
        dif = dif.sum()
        current = new.copy()
        iters += 1
        if iters == 20:
            print 'WARNING: Value function\
                   did not converge!'
            print dif
        print dif
    return new

def calc_trans(current, w, lam, dis, p):
    dat = pd.DataFrame({'v1': current, 'w1': w})
    min_stat = dat.apply(lambda row: mins(row, dat, p), axis=1)
    trans = min_stat * lam / len(current)
    cols = trans.columns
    ind  = trans.index
    trans_mat = trans.as_matrix();
    np.fill_diagonal(trans_mat,0)
    np.fill_diagonal(trans_mat,1 - trans_mat.sum(1))
    trans = pd.DataFrame(trans_mat,index=ind,columns=cols)
    return trans

def val_loop(w, lam, dis, p, init='nope'):
    # This function calls the value function loop

    # INITIAL GUESS
    if type(init) != str:
        current = init
    else:
        current = w.apply(lambda x: x / (1 - dis))

    # MAIN LOOP
    new = val_loop_inner(current, w, lam, dis, p)

    # GET TRANSITIONS
    trans = calc_trans(new, w, lam, dis, p)

    return new, trans

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
vals, trans = val_init(mov_params, dep_stats, 0.15, 0.90, 10)
vals, trans = val_init(mov_params*1.01, dep_stats, 0.15, 0.90, 10, vals)

f = file('trans.pickle','wb')
pickle.dump(trans,f)



