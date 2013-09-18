# This script calls the main estimation loop for discrete version of my model

import pandas as pd
import val_defs as vd
import cit_defs as cd
import collections
import pickle
import math
import est_loop as el
import numpy as np
import time
import random
import csv

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
    first_ff = pd.read_pickle('first_ff.pickle')
    bd = pd.read_pickle('budget_def.pickle')

    # OUTPUT
    timestr = time.strftime("%Y%m%d-%H%M%S")\
        + '_' + str(random.randrange(100000))
    out_file = open('results/out_' + timestr + '.csv','wb')
    out_writer = csv.writer(out_file)

    # GET INITIAL LIKELIHOOD
    init, trans, itrans = vd.val_init(big_mov_params, dep_stats, 0.9, ip, bd, init)
    mlik = []
    for lat in range(2):
        not91 = mov_dat_not91.groupby('au').apply(lambda x: cd.mov_lik(trans, x, lat))
        is91  = mov_dat91.groupby('au').apply(lambda x: cd.mov_lik(itrans, x, lat))
        together = pd.DataFrame({'not91': not91, 'is91': is91}, index=not91.index)
        together = together.fillna(value=1)
        together = together.prod(1)
        mlik.append(together)

    cit_liks, fc_liks, nocit_liks = [], [], []
    for lat in range(2):
        cit_liks.append(citers.groupby('au')\
                    .apply(lambda x: cd.cit_lik_cit(alp, bet, gam, x, dep_year, lat)))
        fc_liks.append(first_cits.groupby('au')\
                    .apply(lambda x: cd.fc_lik(alp, bet, gam,  x, dep_year, lat)))
        nocit_liks.append(nocits.groupby('au')\
                    .apply(lambda x: cd.cit_lik_no_cit(alp, bet, gam, x, dep_year, lat)))

    # CALCULATE 
    lik_pieces = []
    for k in range(2):
        lik_dat = pd.DataFrame(mlik[k], columns=['mlik'])
        lik_dat['cit_liks'] = cit_liks[k]
        lik_dat['fc_liks'] = fc_liks[k]
        lik_dat['nocit_liks'] = nocit_liks[k]
        lik_pieces.append(lik_dat)
    lik = el.recalc_lik(lik_pieces, first_ff, lp)

    # CALL ESTIMATION LOOP
    el.est_loop(lik, lik_pieces, big_mov_params, cit_params,
            lp, init, trans, dep_stats, mov_dat91, mov_dat_not91,
            first_cits, citers, nocits, dep_year,
            out_file, out_writer, first_ff, ip, bd)

