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
from scipy.stats import beta as betad
import adapt
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

def prior(cit_params, big_mov_params, lp, ip):
    # calculates the prior probability
    run_sum = 0
    [alp, gam, bet] = cit_params
    run_sum += betad.logpdf(gam[0],1,2)
    run_sum += betad.logpdf(gam[1],0.125,2)
    return run_sum

def update_cits(cit_params, rnd):
    # updates cit parameters

    # get user jump size
    j = pd.read_csv('jump_size.csv').set_index('block')
    s_alp = list(j.loc['cit_alp'])[0]
    s_bet = list(j.loc['cit_bet'])[0]
    s_gam0 = list(j.loc['cit_gam0'])[0]
    s_gam1 = list(j.loc['cit_gam1'])[0]

    [alp, gam, bet] = cit_params
    alp = alp + random.gauss(0,rnd['alpha'] * s_alp)
    bet = bet + random.gauss(0,rnd['bet'] * s_bet)
    gam[0] = norm.cdf(norm.ppf(gam[0], 0, 1) +
                      random.gauss(0,rnd['gam_0'] * s_gam0), 0, 1)
    gam[1] = norm.cdf(norm.ppf(gam[1], 0, 1) +
                      random.gauss(0,rnd['gam_1'] * s_gam1), 0, 1)
    cit_params_u = [alp, gam, bet]
    return cit_params_u

def update_movs(big_mov_params, ip, rnd):
    # updates mov parameters

    # get user jump size
    j = pd.read_csv('jump_size.csv').set_index('block')
    slo1 = list(j.loc['mov_lo1'])[0]
    slo2 = list(j.loc['mov_lo2'])[0]
    sp = list(j.loc['mov_p'])[0]
    sq = list(j.loc['mov_q'])[0]
    sf = list(j.loc['mov_f'])[0]
    sl = list(j.loc['mov_l'])[0]
    sip = list(j.loc['mov_ip'])[0]

    [mov_params, lam, p] = big_mov_params
    lam[0] = lam[0] + random.gauss(0, rnd['lo1'] * slo1)
    lam[1] = lam[1] + random.gauss(0, rnd['lo2'] * slo2)
    p = 1 + math.exp(math.log(p - 1) + random.gauss(0,rnd['p'] * sp))
    mov_params = mov_params.astype('float64')
    mov_params['qual'] = mov_params['qual']\
                          + random.gauss(0,rnd['qual_co'] * sq)
    mov_params['field'] = mov_params['field']\
                          + random.gauss(0,rnd['field_co'] * sf)
    mov_params['lat'] =  mov_params['lat']\
                          + random.gauss(0,rnd['lat_co'] * sl)
    big_mov_params_u = [mov_params, lam, p]
    ip_u = math.exp(math.log(ip)
                    + random.gauss(0,rnd['ip'] * sip))

    return big_mov_params_u, ip_u

def calc_cit_lik(cit_params, big_mov_params, citers,
                                 nocits, first_cits, lp, lik_pieces,
                                 dep_year, init, first_ff, ip, cit_rnd):
    # Updates cits and recalculates likelihood

    cit_params_u = update_cits(deepcopy(cit_params), cit_rnd)
    big_mov_params_u = deepcopy(big_mov_params)
    lp_u = deepcopy(lp)
    ip_u = deepcopy(ip)
    init_u = deepcopy(init)
    
    cit_liks, fc_liks, nocit_liks = [], [], []
    lik_pieces_u = deepcopy(lik_pieces)
    for lat in range(3):
        cit_liks.append(citers.groupby('au')\
                    .apply(lambda x: cd.cit_lik_cit(cit_params_u[0],
                           cit_params_u[2], cit_params_u[1], x, dep_year, lat, lp_u)))
        fc_liks.append(first_cits.groupby('au')\
                    .apply(lambda x: cd.fc_lik(cit_params_u[0],
                           cit_params_u[2], cit_params_u[1],  x, dep_year, lat, lp_u)))
        nocit_liks.append(nocits.groupby('au')\
                    .apply(lambda x: cd.cit_lik_no_cit(cit_params_u[0],
                           cit_params_u[2], cit_params_u[1], x, dep_year, lat, lp_u)))
        lik_pieces_u[lat]['cit_liks'] = cit_liks[lat]
        lik_pieces_u[lat]['fc_liks'] = fc_liks[lat]
        lik_pieces_u[lat]['nocit_liks'] = nocit_liks[lat]

    lik_u = recalc_lik(lik_pieces_u, first_ff, lp_u)
    lik_u += prior(cit_params_u, big_mov_params_u, lp_u, ip_u)
    
    return lik_u, cit_params_u, big_mov_params_u,\
            lp_u, lik_pieces_u, init_u, ip_u


def init_cond(mean, lp_u, lat):
    """calculates initial latent type multiple for simpson's rule"""
    
    # BOUND DIFFERENCE FROM ZERO
    scale = 4 * lp_u[2] / float(6)
    if lat == 0:
        arg = norm.pdf(-2 * lp_u[2], mean, lp_u[2])
        return scale * arg
    if lat == 1:
        arg = 4 * norm.pdf(0, mean, lp_u[2])
        return scale * arg 
    if lat == 2:
        arg = norm.pdf(2 * lp_u[2], mean, lp_u[2])
        return scale * arg 


def recalc_lik(lik_pieces_u, first_ff, lp_u):
    # recalculates lik from updates lik_pieces

    lik_mid = []
    ff_mean = first_ff['dmean'].apply(lambda x: 0.2 *
                                norm.cdf(lp_u[0] + x * lp_u[1]) - 1)
    for k in range(3):
        lik_pieces_u[k]['ff'] = ff_mean.apply(lambda x:
                                        init_cond(x, lp_u, k))
    lik_mid.append(lik_pieces_u[0].prod(axis = 1))
    lik_mid.append(lik_pieces_u[1].prod(axis = 1))
    lik_mid.append(lik_pieces_u[2].prod(axis = 1))
    lik_big = lik_mid[0] + lik_mid[1] + lik_mid[2]
    try:
        lik_u = lik_big.apply(lambda x: math.log(x)).sum()
    except Exception as e:
        print "WARNING: Error in lik calculation,\
                file est_loop.py, function recalc_lik"
        print e
        lik_u = -1e10
    return lik_u

def calc_lp_lik(cit_params, big_mov_params,
                lp, lik_pieces, init, first_ff, ip):
    # updates lp and recalcs lik

    # get user jump size
    jump = pd.read_csv('jump_size.csv').set_index('block')
    s0 = list(jump.loc['lp0'])[0]
    s1 = list(jump.loc['lp1'])[0]
    s2 = list(jump.loc['lp2'])[0]

    cit_params_u = deepcopy(cit_params)
    big_mov_params_u = deepcopy(big_mov_params)
    init_u = deepcopy(init)
    ip_u = deepcopy(ip)
    lp_u = []
    lp_u.append(deepcopy(lp[0]) + random.gauss(0, s0))
    lp_u.append(deepcopy(lp[1]) + random.gauss(0, s1))
    lp_u.append(math.exp(math.log(deepcopy(lp[2]))
                         + random.gauss(0, s2)))
    lik_pieces_u = deepcopy(lik_pieces)
    lik_u = recalc_lik(lik_pieces_u, first_ff, lp_u)
    lik_u += prior(cit_params_u, big_mov_params_u, lp_u, ip_u)
    return lik_u, cit_params_u, big_mov_params_u,\
            lp_u, lik_pieces_u, init_u, ip_u

def calc_mov_lik(cit_params, big_mov_params,
                 lp, lik_pieces, dep_stats,
                 init, mov_dat91, mov_dat_not91,
                 first_ff, ip, bd, loc_rnd):
    # Updates movs and recalculates likelihood

    cit_params_u = deepcopy(cit_params)
    big_mov_params_u, ip_u = update_movs(deepcopy(big_mov_params),
                                deepcopy(ip), loc_rnd)
    lp_u = deepcopy(lp)
    lik_pieces_u = deepcopy(lik_pieces)
    
    # NEW VAL AND TRANSITIONS
    init_u, trans_u, itrans_u = vd.val_init(big_mov_params_u, dep_stats,
                              0.9, ip_u, bd, deepcopy(init), lp_u)

    # NEW LIKELIHOOD CALCUATION
    mlik = []
    for lat in range(3):
        not91 = mov_dat_not91.groupby('au')\
                .apply(lambda x: cd.mov_lik(trans_u, x, lat))
        is91  = mov_dat91.groupby('au')\
                .apply(lambda x: cd.mov_lik(itrans_u, x, lat))
        together = pd.DataFrame({'not91': not91, 'is91': is91},
                                index=not91.index)
        together = together.fillna(value=1).prod(1)
        mlik.append(together)
        lik_pieces_u[lat]['mlik'] = mlik[lat]
    lik_u = recalc_lik(lik_pieces_u, first_ff, lp_u)
    lik_u += prior(cit_params_u, big_mov_params_u, lp_u, ip_u)
    return lik_u, cit_params_u, big_mov_params_u,\
            lp_u, lik_pieces_u, init_u, ip_u

def est_loop(lik, lik_pieces, big_mov_params, cit_params,
        lp, init, trans, dep_stats, mov_dat91, mov_dat_not91,
        first_cits, citers, nocits, dep_year,
        out_file, out_writer, first_ff, ip, bd, timestr):
    # called by discrete.py, this is the boss of the
    # estimation loop

    cit_tot, lp_tot, mov_tot = 1, 1, 1
    cit_acc, lp_acc, mov_acc = 0, 0, 0
    for k in range(200000):

        tic = clock()
        print bcolors.RED + str(k) + bcolors.ENDC

        if k % 3 == 1:
            print ''.join(['cit ', str(cit_acc / float(cit_tot))])
            cit_tot += 1
            [cit_rnd, loc_rnd] = adapt.get_cov(timestr, k, 'cit')
            lik_u, cit_params_u, big_mov_params_u,\
                    lp_u, lik_pieces_u, init_u, ip_u\
                    = calc_cit_lik(cit_params, big_mov_params, citers,
                                   nocits, first_cits, lp, lik_pieces,
                                   dep_year, init, first_ff, ip, cit_rnd)

        if k % 3 == 0:
            print ''.join(['lp ', str(lp_acc / float(lp_tot))])
            lp_tot += 1
            lik_u, cit_params_u, big_mov_params_u,\
                    lp_u, lik_pieces_u, init_u, ip_u\
                    = calc_lp_lik(cit_params, big_mov_params,
                                  lp, lik_pieces, init, first_ff, ip)

        if k % 3 == 2:
            print ''.join(['mov ', str(mov_acc / float(mov_tot))])
            [cit_rnd, loc_rnd] = adapt.get_cov(timestr, k, 'loc')
            mov_tot += 1
            lik_u, cit_params_u, big_mov_params_u,\
                    lp_u, lik_pieces_u, init_u, ip_u\
                    = calc_mov_lik(cit_params, big_mov_params,
                            lp, lik_pieces, dep_stats,
                            init, mov_dat91, mov_dat_not91,
                            first_ff, ip, bd, loc_rnd)

        print bcolors.BLUE + str(lik) + ', ' + str(lik_u) + bcolors.ENDC

        if math.log(random.random()) < (lik_u - lik):
            print bcolors.PURP + 'ACCEPTED!' + bcolors.ENDC
            [cit_params, big_mov_params, lp, ip]\
                    = [deepcopy(cit_params_u), deepcopy(big_mov_params_u),
                            deepcopy(lp_u), deepcopy(ip_u)]
            init = deepcopy(init_u)
            lik = deepcopy(lik_u)
            lik_pieces = deepcopy(lik_pieces_u)
            if k % 3 == 1:
                cit_acc += 1
            if k % 3 == 0:
                lp_acc += 1
            if k % 3 == 2:
                mov_acc += 1

        # WRITE
        write_me(cit_params, big_mov_params,
                lp, ip, out_writer, out_file)

        toc = clock() - tic
        print bcolors.YEL + str(toc) + bcolors.ENDC

def write_me(cit_params, big_mov_params, lp, ip, out_writer, out_file):
    # writes to file
    [movparams, lam, p] = big_mov_params
    out_writer.writerow([cit_params[0]] + cit_params[1] + [cit_params[2]]
            + list(movparams) + lam + [p] + lp + [ip])
    out_file.flush()
    return 0
