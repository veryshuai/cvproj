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
    vals, trans, itrans, mlik = vm.call_parallel(big_mov_params, dep_stats,
                                            dis, ip, bd, init, lp, n9, is9)
    return vals, trans, itrans, mlik

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

def calc_exp(currents, w, dp, p):
    # caculates expectation part of value function

    dat = pd.DataFrame({'v1': currents, 'w1': w})
    min_stat = dat.apply(lambda row: mins(row, dat, p), axis=1)
    max_stat = dat.apply(lambda row: maxs(row, dat, p), axis=1)
    exp_mat = currents.transpose() \
            + max_stat * (1 + 1 / (float(p) - 1) * min_stat)
    exp_mat = exp_mat.as_matrix()
    exp_mat = exp_mat * dp
    exp = pd.Series(exp_mat.sum(0), index=currents.index)
    return exp

def val_eval(currents, w, dp, lam, dis, p):
    # This function evaluates the value function

    # EXPECTATION 
    exp = calc_exp(currents, w, dp, p)

    # REST
    new = dis * (1 - lam) / (1 - dis * (1 - lam)) * w\
            + dis * lam / (1 - dis * (1 - lam)) * exp
    return new

def val_loop_inner(current, w, dp, lam, dis, p):
    # runs actual val loop
    dif = 1
    iters = 0
    while dif > 1e-1 and iters < 100:
        new = val_eval(current, w, dp, lam, dis, p)
        dif = pow(new - current,2)
        dif = dif.sum()
        current = new.copy()
        iters += 1
        if iters == 100:
            print 'WARNING: Value function\
                   did not converge!'
            print dif
    return new

def calc_trans(current, w, dp, lam, dis, p):
    dat = pd.DataFrame({'v1': current, 'w1': w})
    min_stat = dat.apply(lambda row: mins(row, dat, p), axis=1)
    trans = min_stat * lam
    cols = trans.columns
    ind  = trans.index
    trans_mat = trans.as_matrix() * dp
    np.fill_diagonal(trans_mat,0)
    np.fill_diagonal(trans_mat,1 - trans_mat.sum(1))
    trans = pd.DataFrame(trans_mat,index=ind,columns=cols)
    return trans

def val_loop(w, dp, lam, dis, p, ip, bd, init='nope'):
    # This function calls the value function loop

    # INITIAL GUESS
    if type(init) != str:
        current = init
    else:
        current = w.apply(lambda x:  x)

    # MAIN LOOP
    new = val_loop_inner(current, w, dp, lam, dis, p)

    # GET TRANSITIONS
    trans = calc_trans(new, w, dp, lam, dis, p)
    # instrument transisitons
    insw = pd.DataFrame({'w': w.sort_index(),
                        'bd': bd.sort_index()},
                        index = w.index)
    insw = insw.apply(lambda x: x['w'] *
                      math.exp(- ip * x['bd']), axis=1)
    insw['OTHER'] = w['OTHER']
    ins_trans = calc_trans(new, insw, dp, lam, dis, p) 

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
    q = mp['wqual']
    f = mp['field']
    l = mp['lat']

    # CALCULATE WAGE
    wq = q * dep['dep_qual']
    wq = 0
    wf = f * wd(field, dep['dmean'])
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
