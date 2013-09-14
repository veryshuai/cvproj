# This file runs the large estimation loop,
# including updateing parameters and recording
# acceptances

import pandas as pd
import val_defs as vd
import cit_defs as cd
import collections
import pickle
import math
import random

def update_cits(cit_params):
    # updates cit parameters

    [alp, gam, bet] = cit_params
    for qual in range(3):
        for field in range(2):
            for lat in range(2):
                alp[qual][field][lat]\
                        = math.exp(math.log(alp[qual][field][lat])
                                   + random.gauss(0,0.1))
                gam[qual][field][lat]\
                        = math.exp(math.log(gam[qual][field][lat])
                                   + random.gauss(0,0.1))
    bet = math.exp(math.log(bet) + random.gauss(0,0.1))
    cit_params_u = [alp, gam, bet]
    return cit_params_u

def est_loop(lik, lik_pieces, big_mov_params, cit_params,
        lp, init, trans, dep_stats, mov_dat,
        first_cits, citers, nocits, dep_year)
    # called by discrete.py, this is the boss of the
    # estimation loop

    for k in range(20000):
        # if k % 3 == 0:
            # update cit_params
        cit_params_u = update_cits(cit_params.copy())
        cit_liks, fc_liks, nocit_liks = [], [], []
        lik_pieces_u = lik_pieces[:]
        for lat in range(2):
            cit_liks.append(citers.groupby('au')\
                        .apply(lambda x: cd.cit_lik_cit(alp, bet, gam, x, dep_year, lat)))
            fc_liks.append(first_cits.groupby('au')\
                        .apply(lambda x: cd.fc_lik(alp, bet, gam,  x, dep_year, lat)))
            nocit_liks.append(nocits.groupby('au')\
                        .apply(lambda x: cd.cit_lik_no_cit(alp, bet, gam, x, dep_year, lat)))
            lik_pieces_u[lat]['cit_liks'] = cit_liks[lat]
            lik_pieces_u[lat]['fc_liks'] = fc_liks[lat]
            lik_pieces_u[lat]['nocit_liks'] = nocit_liks[lat]






