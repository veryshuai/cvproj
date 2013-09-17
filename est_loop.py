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
from time import clock, time
from copy import copy, deepcopy
from scipy.stats import norm
import numpy as np

# COLOR TEXT PRINTING
# http://stackoverflow.com/questions/287871/print-in-terminal-with-colors-using-python
class bcolors:
    PURP = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YEL = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'

    def disable(self):
        self.PURP = ''
        self.BLUE = ''
        self.GREEN = ''
        self.YEL = ''
        self.RED = ''
        self.ENDC = ''

def update_cits(cit_params):
    # updates cit parameters

    [alp, gam, bet] = cit_params
    for qual in range(1): #all qualities share parameters!
        for field in range(2):
            for lat in range(1):
                alp[qual][field][lat]\
                    = alp[qual][field][lat] + random.gauss(0,.01)
                bet[qual][field][lat]\
                    = bet[qual][field][lat] + random.gauss(0,.01)
                gam[qual][field][lat]\
                    = norm.cdf(norm.ppf(gam[qual][field][lat],
                        0, 1) + random.gauss(0, 0.1), 0, 1)
    cit_params_u = [alp, gam, bet]
    return cit_params_u

def update_movs(big_mov_params):
    # updates mov parameters

    [mov_params, lam, p] = big_mov_params
    lam = norm.cdf(norm.ppf(lam, 0, 1) 
                    + random.gauss(0, 0.05), 0, 1)
    p = math.exp(math.log(p) + random.gauss(0,0.01))
    mov_params = mov_params.astype('float64')
    mov_params['qual'] = 1 # mov_params['qual'] + random.gauss(0,0.01)
    mov_params['field'] = mov_params['field'] + random.gauss(0,0.01)
    # mov_params['lat'] = mov_params['lat'] + random.gauss(0,0.05)

    big_mov_params_u = [mov_params, lam, p]
    return big_mov_params_u

def calc_cit_lik(cit_params, big_mov_params, citers,
                                 nocits, first_cits, lp, lik_pieces,
                                 dep_year, mult_by, init):
    # Updates cits and recalculates likelihood

    cit_params_u = update_cits(deepcopy(cit_params))
    big_mov_params_u = deepcopy(big_mov_params)
    lp_u = deepcopy(lp)
    init_u = deepcopy(init)
    
    cit_liks, fc_liks, nocit_liks = [], [], []
    lik_pieces_u = deepcopy(lik_pieces)
    for lat in range(1):
        cit_liks.append(citers.groupby('au')\
                    .apply(lambda x: cd.cit_lik_cit(cit_params_u[0],
                           cit_params_u[2], cit_params_u[1], x, dep_year, lat)))
        fc_liks.append(first_cits.groupby('au')\
                    .apply(lambda x: cd.fc_lik(cit_params_u[0],
                           cit_params_u[2], cit_params_u[1],  x, dep_year, lat)))
        nocit_liks.append(nocits.groupby('au')\
                    .apply(lambda x: cd.cit_lik_no_cit(cit_params_u[0],
                           cit_params_u[2], cit_params_u[1], x, dep_year, lat)))
        lik_pieces_u[lat]['cit_liks'] = cit_liks[lat]
        lik_pieces_u[lat]['fc_liks'] = fc_liks[lat]
        lik_pieces_u[lat]['nocit_liks'] = nocit_liks[lat]

    lik_u = recalc_lik(lik_pieces_u, lp_u, mult_by)
    
    return lik_u, cit_params_u, big_mov_params_u,\
            lp_u, lik_pieces_u, init_u

def recalc_lik(lik_pieces_u, lp_u, mult_by):
    # recalculates lik from updates lik_pieces

    lik_mid = []
    # not_lp = mult_by.apply(lambda x: max(1 - lp_u, x))
    # lik_pieces_u[0]['not_lp'] = not_lp
    lik_mid.append(lik_pieces_u[0].prod(axis = 1))
    # lik_mid.append(lik_pieces_u[1].prod(axis = 1) * lp_u)
    # lik_big = lik_mid[0] + lik_mid[1]
    lik_big = lik_mid[0]
    try:
        lik_u = lik_big.apply(lambda x: math.log(x)).sum()
    except Exception as e:
        print e
        lik_u = -1e10
    return lik_u

def calc_lp_lik(cit_params, big_mov_params,
                lp, lik_pieces, mult_by, init):
    # updates lp and recalcs lik
    cit_params_u = deepcopy(cit_params)
    big_mov_params_u = deepcopy(big_mov_params)
    init_u = deepcopy(init)
    lp_u = 0 #norm.cdf(norm.ppf(deepcopy(lp), 0, 1) 
             #       + random.gauss(0, 1), 0, 1)
    lik_pieces_u = deepcopy(lik_pieces)
    lik_u = recalc_lik(lik_pieces_u, lp_u, mult_by)
    return lik_u, cit_params_u, big_mov_params_u,\
            lp_u, lik_pieces_u, init_u

def calc_mov_lik(cit_params, big_mov_params,
                 lp, lik_pieces, dep_stats, mult_by,
                 init, mov_dat):
    # Updates movs and recalculates likelihood

    cit_params_u = deepcopy(cit_params)
    big_mov_params_u = update_movs(deepcopy(big_mov_params))
    lp_u = deepcopy(lp)
    lik_pieces_u = deepcopy(lik_pieces)
    
    # NEW VAL AND TRANSITIONS
    init_u, trans_u = vd.val_init(big_mov_params_u, dep_stats,
                              0.9, deepcopy(init))

    # NEW LIKELIHOOD CALCUATION
    mlik = []
    for lat in range(1):
        mlik.append(mov_dat.groupby('au')\
                .apply(lambda x: cd.mov_lik(trans_u, x, lat)))
        lik_pieces_u[lat]['mlik'] = mlik[lat]
    lik_u = recalc_lik(lik_pieces_u, lp_u, mult_by)
    return lik_u, cit_params_u, big_mov_params_u,\
            lp_u, lik_pieces_u, init_u

def est_loop(lik, lik_pieces, big_mov_params, cit_params,
        lp, init, trans, dep_stats, mov_dat,
        first_cits, citers, nocits, dep_year,
        mult_by, out_file, out_writer):
    # called by discrete.py, this is the boss of the
    # estimation loop

    cit_tot, lp_tot, mov_tot = 1, 1, 1
    cit_acc, lp_acc, mov_acc = 0, 0, 0
    for k in range(20000):

        tic = clock()
        print bcolors.RED + str(k) + bcolors.ENDC

        if k % 3 == 0:
            print ''.join(['cit ', str(cit_acc / float(cit_tot))])
            cit_tot += 1
            lik_u, cit_params_u, big_mov_params_u,\
                    lp_u, lik_pieces_u, init_u\
                    = calc_cit_lik(cit_params, big_mov_params, citers,
                                   nocits, first_cits, lp, lik_pieces,
                                   dep_year, mult_by, init)

        if k % 3 == 1:
        #    print ''.join(['lp ', str(lp_acc / float(lp_tot))])
        #    lp_tot += 1
        #    lik_u, cit_params_u, big_mov_params_u,\
        #            lp_u, lik_pieces_u, init_u\
        #            = calc_lp_lik(cit_params, big_mov_params,
        #                          lp, lik_pieces, mult_by, init)
            lik_u = -1e6

        if k % 3 == 2:
            print ''.join(['mov ', str(mov_acc / float(mov_tot))])
            mov_tot += 1
            lik_u, cit_params_u, big_mov_params_u,\
                    lp_u, lik_pieces_u, init_u\
                    = calc_mov_lik(cit_params, big_mov_params,
                            lp, lik_pieces, dep_stats, mult_by,
                            init, mov_dat)

        print bcolors.BLUE + str(lik) + ', ' + str(lik_u) + bcolors.ENDC

        if math.log(random.random()) < (lik_u - lik):
            print bcolors.PURP + 'ACCEPTED!' + bcolors.ENDC
            [cit_params, big_mov_params, lp]\
                    = [deepcopy(cit_params_u), deepcopy(big_mov_params_u),
                            deepcopy(copy(lp_u))]
            init = deepcopy(init_u)
            lik = deepcopy(lik_u)
            lik_pieces = deepcopy(lik_pieces_u)
            if k % 3 == 0:
                cit_acc += 1
            if k % 3 == 1:
                lp_acc += 1
            if k % 3 == 2:
                mov_acc += 1

        # WRITE
        write_me(cit_params, big_mov_params,
                lp, out_writer, out_file)

        toc = clock() - tic
        print bcolors.YEL + str(toc) + bcolors.ENDC

def write_me(cit_params, big_mov_params, lp, out_writer, out_file):
    # writes to file

    # writeable form
    cit_write = []
    for pnum in range(3):
        for qual in range(1):
            for field in range(2):
                for lat in range(1):
                    if field == 0 and lat == 1:
                        pass
                    else:
                        cit_write.append(cit_params[pnum][qual][field][lat])
    [movparams, lam, p] = big_mov_params
    out_writer.writerow(cit_write + list(movparams) + [lam] + [p] + [lp])
    out_file.flush()
    return 0
