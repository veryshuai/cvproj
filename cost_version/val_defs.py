# This file contains definition for value function
# iteration in the discrete version of my model.

import pandas as pd
import numpy as np
import cyfuncs as cyf
import pickle
import val_mp as vm
import math
import collections

#From stefan at stack overflow:
#http://stackoverflow.com/questions/3009935/looking-for-a-good-python-tree-data-structure
def tree():
    return collections.defaultdict(tree)

def val_init(big_mov_params, dep_stats, dis, ip, bd, init, lp, n9, is9):
    # initializes value function iteration
    vals, trans, itrans, mlik, flag = vm.call_parallel(big_mov_params, dep_stats,
                                         dis, ip, bd, init, lp, n9, is9)
    # FOR DEBUGGING
    #vm.val_calc(1, 1, 1, big_mov_params, dep_stats, dis, ip, bd, init, lp)
    return vals, trans, itrans, mlik, flag

def exp_sum(v, dat):
    """exponentiates everything in the correct way for val function """

    out = dat.apply(lambda x: math.exp(v[0] + v[1])
                    + math.exp(x[0] + x[1]), axis=1)
    return out


def calc_rat(x,v):
    """calculates ratio, avoids double calculation to save time"""
    new_dep = math.exp(x[0] + x[1])
    old_dep = math.exp(v[0] + v[1])
    rat = new_dep / (old_dep + new_dep)
    return rat


def exp_rat(v, dat):
    """returns logit prob"""
    out = dat.apply(lambda x: calc_rat(x,v), axis=1)
    return out


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

def calc_exp(currents, w, p, lam):
    """caculates expectation part of value function"""

    #DATAFRAME WITH VALS AND PAYOFFS
    dat = pd.DataFrame({'v1': currents, 'w1': w})
    no_cost_sums = dat.apply(lambda row: math.exp(row[0] + row[1]), axis=1)
    cost_sums = dat.apply(lambda row: math.exp(row[0] + row[1] - lam), axis=1)

    #REPEAT DATA FRAME, FILL DIAGONAL
    exp_mat = np.repeat([cost_sums.values],len(cost_sums),axis=0)
    np.fill_diagonal(exp_mat,no_cost_sums)

    #SUM AND RETURN
    exp = pd.Series(exp_mat.sum(0), index=currents.index).apply(math.log)

    return exp

def val_eval(currents, w, lam, dis, p):
    """This function evaluates the value function"""

    # MULT EXPECTATION BY DISCOUNT 
    new = dis * calc_exp(currents, w, p, lam)

    return new

def val_loop_inner(current, w, lam, dis, p):
    # runs actual val loop
    dif = 1
    iters = 0
    while dif > 1e-5 and iters < 500:
        new = val_eval(current, w, lam, dis, p)
        dif = pow(new - current,2)
        dif = dif.sum()
        current = new.copy()
        iters += 1
        if iters == 500:
            print 'WARNING: Value function\
                   did not converge!'
            print dif
    return new

def calc_trans(current, w, lam, dis, p):
    """Given the values, calculate transition probs"""

    #DATAFRAME WITH VALS AND PAYOFFS
    dat = pd.DataFrame({'v1': current, 'w1': w})
    no_cost_sums = dat.apply(lambda row: row[0] + row[1], axis=1)
    cost_sums = dat.apply(lambda row: row[0] + row[1] - lam, axis=1)

    #REPEAT DATA FRAME, FILL DIAGONAL
    exp_mat = np.repeat([cost_sums.values],len(cost_sums),axis=0)
    np.fill_diagonal(exp_mat,no_cost_sums)

    #GET PROBABILITIES
    row_max = exp_mat.max(axis=1, keepdims=True)
    trans = np.exp(exp_mat - row_max) / np.exp(exp_mat - row_max).sum(axis=1,keepdims=True)

    #ADD LABELS
    cols = dat.index
    ind  = dat.index
    trans_mat = trans
    trans = pd.DataFrame(trans_mat,index=ind,columns=cols)
    
    return trans

def val_loop(w, lam, dis, p, ip, bd, init='nope'):
    # This function calls the value function loop

    # INITIAL GUESS
    if type(init) != str:
        current = init
    else:
        current = w.apply(lambda x:  x)

    # MAIN LOOP
    new = val_loop_inner(current, w, lam, dis, p)

    # GET TRANSITIONS
    trans = calc_trans(new, w, lam, dis, p)
    # instrument transisitons
    insw = pd.DataFrame({'w': w.sort_index(),
                        'bd': bd.sort_index()},
                        index = w.index)
    insw = insw.apply(lambda x: x['w'] *
                      math.exp(- ip * x['bd']), axis=1)
    insw['OTHER'] = w['OTHER']
    ins_trans = calc_trans(new, insw, lam, dis, p) 

    return new, trans, ins_trans

def wd(ind, dep):
    # peforms distance calculation for wage
    out = dep.apply(lambda x: pow(ind - x,2))
    return out

def calc_depprob(mp, dep, qual, field, lat, qp):
    # returns probability of getting an offer from
    # each dep for qual

    # EASY PARAMETER REFERENCE
    q = mp['qual']

    qual_dif = dep['dep_qual'].apply(lambda x:
            math.exp(q * (qual - x) ** 2))
    vs = qual_dif.values
    depprobs = np.vstack(tuple([vs] * len(vs)))
    np.fill_diagonal(depprobs,0)
    depprobs = depprobs / depprobs.sum(1)
    return depprobs

def calc_wage(mp, dep, qual, field, lat, qp):
    # returns wage at each of the departments

    # EASY PARAMETER REFERENCE
    q = mp['qual'] * 2 - 1
    f = mp['field']
    l = mp['lat']

    # CALCULATE WAGE
    wq = q * qual * dep['dep_qual']
    wf = f * field * dep['dmean']
    # quadrature points 
    wl = l * dep['dmean'] * qp[lat]
    w_mid = wq + wf + wl
    w = w_mid.apply(lambda x: math.exp(x))

    return w

def reset(vals, trans, itrans, mlik):
    # RESET INITIAL STARTING POINT
    
    f = file('trans.pickle','wb')
    pickle.dump(trans,f)
    f.close()
    
    f = file('val_init.pickle','wb')
    pickle.dump(vals,f)
    f.close()

    f = file('itrans.pickle','wb')
    pickle.dump(itrans,f)
    f.close()

    f = file('mlik.pickle','wb')
    pickle.dump(mlik,f)
    f.close()

    return 0
