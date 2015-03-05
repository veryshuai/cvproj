# This script calls the main estimation loop for discrete version of my model

import pandas as pd
import val_defs as vd
import cit_mp as cm
import cit_defs as cd
import pickle
import math
import est_loop as el
import numpy as np
import time
import random
import csv
import cProfile
import collections

#From stefan at stack overflow:
#http://stackoverflow.com/questions/3009935/looking-for-a-good-python-tree-data-structure
def tree():
    return collections.defaultdict(tree)

def main(cit_params, big_mov_params, lp, ip):

    [alp, gam, bet] = cit_params
    [mov_params, lo, p] = big_mov_params

    # READ IN OTHER DATA
    dep_stats = pd.read_pickle('dep_list.pickle').set_index('dep')
    f = file('val_init.pickle','rb')
    init = pickle.load(f)
    mov_dat91 = pd.read_pickle('mov_dat91.pickle')
    mov_dat_not91 = pd.read_pickle('mov_dat_not91.pickle')
    first_cits = pd.read_pickle('first_cits.pickle')
    citers = pd.read_pickle('citers.pickle')
    nocits = pd.read_pickle('nocits.pickle')
    dep_year = pd.read_pickle('dep_years.pickle')
    dep_reg = pd.read_pickle('dep_reg.pickle')
    dep_nat = pd.read_pickle('dep_nat.pickle')
    first_ff = pd.read_pickle('first_ff.pickle')
    bd = pd.read_pickle('budget_def.pickle')

    # OUTPUT
    timestr = time.strftime("%Y%m%d-%H%M%S")\
        + '_' + str(random.randrange(100000))
    out_file = open('results/out_' + timestr + '.csv','wb')
    out_writer = csv.writer(out_file)

    # GET INITIAL LIKELIHOOD
    init, trans, itrans, mlik, flag = vd.val_init(big_mov_params, dep_stats,
                                      0.95, ip, bd, init, lp,
                                      mov_dat_not91, mov_dat91)
    trans[1][1][1].to_csv('test.csv')
    vd.reset(init, trans, itrans, mlik)

    cit_liks, fc_liks, nocit_liks\
            = cm.call_parallel(cit_params, dep_year, dep_reg,
                               dep_nat, lp, citers, first_cits, nocits)

    # CALCULATE 
    lik_pieces = []
    for k in range(4):
        lik_dat = pd.DataFrame(mlik[k], columns=['mlik'])
        lik_dat['cit_liks'] = cit_liks[k]
        lik_dat['fc_liks'] = fc_liks[k]
        lik_dat['nocit_liks'] = nocit_liks[k]
        lik_pieces.append(lik_dat)
    lik = el.prior(cit_params, big_mov_params, lp, ip)
    lik += el.recalc_lik(lik_pieces, first_ff, lp)

    # CHECK FOR ERROR
    if flag == 1:
        lik = -1e10

    # pr.dump_stats('profile.out')
    # CALL ESTIMATION LOOP
    el.est_loop(lik, lik_pieces, big_mov_params, cit_params,
            lp, init, trans, dep_stats, mov_dat91, mov_dat_not91,
            first_cits, citers, nocits, dep_year, dep_reg,
            dep_nat, out_file, out_writer, first_ff, ip, bd, timestr)

