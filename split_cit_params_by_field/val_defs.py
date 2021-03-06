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

def exp_sum(v, dat):
    """returns logit expectation"""
    out = dat.apply(lambda x: math.log(math.exp(v[0] + v[1])
                    + math.exp(x[0] + x[1])), axis=1)
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

def calc_exp(currents, w, p):
    # caculates expectation part of value function

    dat = pd.DataFrame({'v1': currents, 'w1': w})
    exp_mat = dat.apply(lambda row: exp_sum(row, dat), axis=1)
    exp_mat = exp_mat / float(dat.shape[0] - 1)
    exp_mat = exp_mat.as_matrix()
    np.fill_diagonal(exp_mat,0)
    exp = pd.Series(exp_mat.sum(0), index=currents.index)
    return exp

def val_eval(currents, w, lam, dis, p):
    # This function evaluates the value function

    # EXPECTATION 
    exp = calc_exp(currents, w, p)

    # REST
    new = dis * (1 - lam) / float(1 - dis * (1 - lam)) * w\
            + dis * lam / float(1 - dis * (1 - lam)) * exp
    return new

def val_loop_inner(current, w, lam, dis, p):
    # runs actual val loop
    dif = 1
    iters = 0
    while dif > 1e-2 and iters < 100:
        new = val_eval(current, w, lam, dis, p)
        dif = pow(new - current,2)
        dif = dif.sum()
        current = new.copy()
        iters += 1
        if iters == 100:
            print 'WARNING: Value function\
                   did not converge!'
            print dif
    return new

def calc_trans(current, w, lam, dis, p):
    dat = pd.DataFrame({'v1': current, 'w1': w})
    rat_mat = dat.apply(lambda row: exp_rat(row, dat), axis=1)
    trans = rat_mat * lam / float(dat.shape[0] - 1)
    cols = trans.columns
    ind  = trans.index
    trans_mat = trans.as_matrix()
    np.fill_diagonal(trans_mat,0)
    np.fill_diagonal(trans_mat,1 - trans_mat.sum(1))
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
    q = mp['qual']
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
