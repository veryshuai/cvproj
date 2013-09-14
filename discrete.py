# This script calls the main estimation loop for discrete version of my model

import pandas as pd
import val_defs as vd
import cit_defs as cd
import collections
import pickle
import math
import est_loop as el

#From stefan at stack overflow:
#http://stackoverflow.com/questions/3009935/looking-for-a-good-python-tree-data-structure
def tree():
    return collections.defaultdict(tree)

def main():

    #INITIAL CIT PARAMETERS (TO BE MOVED)
    alp = tree()
    gam = tree()
    for qual in range(3):
        for field in range(2):
            for lat in range(2):
                alp[qual][field][lat] = 0.1
                gam[qual][field][lat] = 0.1
    bet = 100

    # INITIAL MOV PARAMETERS (TO BE MOVED)
    mov_params = pd.Series({'qual': 1, 'field': 1, 'lat': 1})

    # OTHER PARAMETERS (TO BE MOVED)
    lp = 0.1 #latent type probability
    lo = 0.15 #offer arrival rate
    p = 10 #signing bonus distribution parameter

    # PUT PARAMS INTO BOXES FOR EASY MOVING
    big_mov_params = [mov_params, lo, p]
    cit_params = [alp, gam, bet]

    # READ IN OTHER DATA
    dep_stats = pd.read_pickle('dep_list.pickle').set_index('dep')
    f = file('val_init.pickle','rb')
    init = pickle.load(f)
    mov_dat = pd.read_pickle('mov_dat.pickle')
    first_cits = pd.read_pickle('first_cits.pickle')
    citers = pd.read_pickle('citers.pickle')
    nocits = pd.read_pickle('nocits.pickle')
    dep_year = pd.read_pickle('dep_years.pickle')

    # GET INITIAL LIKELIHOOD
    init, trans = vd.val_init(big_mov_params, dep_stats, 0.9, init)
    mlik = []
    for lat in range(2):
        mlik.append(mov_dat.groupby('au').apply(lambda x: cd.mov_lik(trans, x, lat)))

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
        lik_dat = pd.DataFrame(mlik[k], columns='mlik')
        lik_dat['cit_liks'] = cit_liks[k]
        lik_dat['fc_liks'] = fc_liks[k]
        lik_dat['nocit_liks'] = nocit_liks[k]
        lik_pieces.append(lik_dat)
    lik_mid = []
    lik_mid.append(lik_pieces[0].prod(axis = 1) * (1 - lp))
    lik_mid.append(lik_pieces[1].prod(axis = 1) * lp)
    lik_big = lik_pieces[0] + lik_pieces[1]
    lik = lik_big.apply(lambda x: math.log(x)).sum()

    # CALL ESTIMATION LOOP
    el.est_loop(lik, lik_pieces, big_mov_params, cit_params,
            lp, init, trans, dep_stats, mov_dat,
            first_cits, citers, nocits, dep_year)

main()
