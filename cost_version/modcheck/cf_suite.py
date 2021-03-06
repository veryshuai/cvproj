# This file contains definitions for functions related to running counterfactuals

import val_defs as vd
import random
from scipy.stats import norm
import collections
import pandas as pd
from copy import copy, deepcopy
import random
import pickle
import math
import time
import csv
import numpy as np

#From stefan at stack overflow:
#http://stackoverflow.com/questions/3009935/looking-for-a-good-python-tree-data-structure
def tree():
    return collections.defaultdict(tree)

def make_lat(row, lp, qp): 
    """ stochastically assigns latent type """

    # ACTUAL LATENT TYPE
    true_lat = random.gauss(lp[0] * row['dep_qual'] 
            + lp[1] * row['dmean'], lp[2])

    # APPROXIMATE TYPE FOR MOVING DECISION
    difarray = np.array((true_lat - qp) ** 2)
    close_lat = np.argmin(difarray)

    return pd.Series([true_lat, close_lat])

def make_int(field, cp): 
    """ stochastically assigns interest """

    if random.random() < cp[1][field]:
        return 1
    else:
        return 0

def make_moves(r, trans):
    dep_list = [r['dep'].iat[0]]
    year_list = [r['date'].iat[0]]
    t = trans[r['qual'].iat[0]][r['isField'].iat[0]][r['closelat']\
            .iat[0]]
    while year_list[-1] < 2000:
        tr = t.loc[dep_list[-1]].cumsum()
        rnd = random.random()
        truth = tr > rnd
        next_dep = tr[truth].index[0]
        dep_list.append(next_dep)
        year_list.append(year_list[-1] + 1)
    return pd.DataFrame({'dep': dep_list, 'yr': year_list})

def u_cit(r, kf, nf, cp, yr, qp):
    """Randomly decides whether each author cited the paper"""
    
    # CHECK FOR INTEREST AND PREVIOUS CITE
    if r['isInt'].iat[0] == 0:
        return 0
    if r['citer'].iat[0] == 1:
        return 1

    # GET KNOWFRACS
    dep = r['dep'][r['year'] == yr].iat[0]
    nat = r['nat'][r['year'] == yr].iat[0]
    try:
        pkf = kf.loc[dep]
        pnf = nf.loc[nat]
    except Exception as e:
        print e
        pkf = 0
        pnf = 0

    # GET CIT PROB
    alp = cp[0][0]
    bet0 = cp[2][0]
    bet1 = 0 #cp[3][0]
    quad = int(r['closelat'].iat[0])
    arg = math.exp(-(alp + bet0 * pkf
            + bet1 * pnf + qp[quad]))
    prob = (1 / (1 + arg))

    # U CITE BRO?
    if random.random() < prob:
        return 1
    else:
        return 0

def erg_iter(t):
    """Finds erg distribution from a trans matrix"""

    dif = 1 
    dist = pd.Series(np.ones(t.shape[0]),index=t.index)
    dist = dist / dist.count()
    while dif > 1e-4:
        old = deepcopy(dist)
        dist = np.dot(dist.T,t)
        dif = np.linalg.norm(dist - old)
    return dist


def find_erg(trans):
    """This function finds the long run distributions for a particular
    set of transition matrices"""
    
    erg = tree()
    for qual in range(2): 
        for field in range(2):
            for lt in range(4):
                erg[qual][field][lt] = erg_iter(trans[qual][field][lt]) 

    return erg

def make_init(r, erg):
    e = erg[r['qual'].iat[0]][r['isField'].iat[0]][r['closelat']\
            .iat[0]]
    tr = e.cumsum()
    rnd = random.random()
    truth = tr > rnd
    init_dep = tr[truth].index[0]
    return init_dep

def offer_cf(lo_cf, cit_params, big_mov_params,
             lp, init, ip, dep_stats, bd, aut_pan,
             n9, is9, qp):
    """ Simulates the evolution of knowledge
    spread with different offer frequency """

    # INSERT COUNTERFACTUAL OFFER PROBABILITY
    print 'BEGIN WITH VALS'
    big_mov_params = [big_mov_params[0], lo_cf, big_mov_params[2]]
    init, trans, itrans, mlik, flag = vd.val_init(big_mov_params, dep_stats,
                                      0.95, ip, bd, init, lp, n9, is9)
    vd.reset(init, trans, itrans, mlik)

    # FIND LONG-RUN DISTRIBUTIONS
    erg = find_erg(trans)

    # ASSIGN DEPARTMENTS
        

    # ASSIGN LATENT TYPE AND INTEREST TO 1986 AUTHORS
    aut_pan = aut_pan[aut_pan['date'] == 1987]
    latcomb = aut_pan.apply(lambda row: make_lat(row, lp, qp), 
                             axis=1)
    aut_pan['truelat'] = latcomb[0]
    aut_pan['closelat'] = latcomb[1]
    aut_pan['isInt'] = aut_pan['isField']\
            .apply(lambda x: make_int(x, cit_params))
    initdep = aut_pan.groupby('au').apply(lambda x:
                                          make_init(x, erg))
    aut_pan = aut_pan.set_index('au')
    aut_pan['dep'] = initdep
    aut_pan = aut_pan.reset_index()
    aut_pan['nat'] = 'USA'

    # SIMULATE MOVES BETWEEN DEPARTMENTS
    print 'WORKING ON MOVES'
    moves = aut_pan.groupby('au').apply(lambda x:
                                          make_moves(x, trans))\
                                 .reset_index()
    moves = pd.merge(moves, aut_pan, on='au')
    moves = moves[['au', 'level_1','dep_x', 'nat','isField','truelat','closelat','isInt']]
    moves.columns = ['au', 'year', 'dep', 'nat', 'isField', 'truelat','closelat','isInt']

    # CALCULATE TRUE MOVE PERCENTAGE
    moves['next_dep'] = moves.groupby('au')['dep'].apply(lambda x: x.shift(-1))
    non_moves = moves[moves['next_dep'] == moves['dep']]['next_dep'].count()
    tot_moves = moves['next_dep'].count()
    movfrac = 1 - non_moves / float(tot_moves)
    print 'Fraction of move years: %.2f' % (movfrac)

    # SIMULATE SPREAD OF KNOWLEDGE THROUGH DEPARTMENTS
    print 'NOW ON CITS'
    cit_evol = moves
    cit_evol['citer'] = 0
    cit_fracs = []
    dep_fracs = []
    dep_sds   = []
    dep_cfv   = []
    nat_fracs = []
    for year in range(int(cit_evol['year'].min()+1), int(cit_evol['year'].max()+1)):
        #knowledge fractions
        kf = cit_evol[cit_evol['year'] == year- 1].groupby('dep')['citer'].mean() 
        nf = cit_evol[cit_evol['year'] == year- 1].groupby('nat')['citer'].mean() 
        # get new cites
        cit_list = cit_evol.groupby('au')\
                            .apply(lambda r: u_cit(r, kf, nf, cit_params, year, qp))
        cit_evol = pd.merge(cit_evol, pd.DataFrame(cit_list).reset_index(), on='au')
        cit_evol['citer'] = cit_evol[0]
        cit_evol = cit_evol.drop(0, axis=1)
        cit_fracs.append(cit_evol.groupby('au')['citer'].max().describe()['mean'])
        dep_fracs.append(cit_evol[cit_evol['year'] == year].groupby('dep')['citer'].max().describe()['mean'])
        sd = cit_evol[cit_evol['year'] == year].groupby('dep')['citer'].mean().describe()['std']
        mean = cit_evol[cit_evol['year'] == year].groupby('dep')['citer'].mean().describe()['mean']
        dep_sds.append(sd)
        dep_cfv.append(sd/mean)

    return [cit_fracs, dep_fracs, dep_sds, dep_cfv]

def new_rand_params(d, ds):
    """ takes converged posterior and draws a random parameter vector"""

    # RANDOM PARAMETER VECTOR
    ch = d.iloc[random.randrange(ds)]
    cit_params = [[ch['alp']], 
                  [ch[' gam0'], ch[' gam1']],
                  [ch[' bet']]]
    mov_params = pd.Series({'field':ch[' field_co'],
                            'lat': ch[' lat_co'],
                            'qual': ch[' qual_co']})
    big_mov_params = [mov_params, ch[' lo'],
                      ch[' p']]
    lp = [ch[' lat_prob1'],
          ch[' lat_prob2'],
          ch[' lat_prob3']]
    ip = ch[' ip']

    return cit_params, big_mov_params, lp, ip


def run_cf():
    """ reads from a results file, and calls
        counterfactual generation program """

    # LOAD PARAMETERS
    d = pd.read_csv('out.csv')
    ds = d.shape[0]


    # QUAD POINTS (I STILL DONT WANT TO DO A DIFFERENT VAL
    # FUNCTION FOR ALL 3000 TYPES IN THE DATA!
    qa = [4 * math.sqrt(3 - 2 * math.sqrt(6 / float(5))) / float(7),
            4 * math.sqrt(3 + 2 * math.sqrt(6 / float(5))) / float(7)]
    qp =  [-qa[1], -qa[0], qa[0], qa[1]]

    # LOAD DATA
    f = file('val_init.pickle','rb')
    init = pickle.load(f)
    dep_stats = pd.read_pickle('dep_list.pickle').set_index('dep')
    aut_pan = pd.read_pickle('initial_panel.pickle')
    mov_dat91 = pd.read_pickle('mov_dat91.pickle')
    mov_dat_not91 = pd.read_pickle('mov_dat_not91.pickle')
    first_cits = pd.read_pickle('first_cits.pickle')
    bd = pd.read_pickle('budget_def.pickle')

    # WRITE 
    timestr = time.strftime("%Y%m%d-%H%M%S")\
        + '_' + str(random.randrange(100000))
    sp0_file = open('results/sp0_' + timestr + '.csv','wb')
    sp0_writer = csv.writer(sp0_file)
    sp05_file = open('results/sp05_' + timestr + '.csv','wb')
    sp05_writer = csv.writer(sp05_file)
    sp10_file = open('results/sp10_' + timestr + '.csv','wb')
    sp10_writer = csv.writer(sp10_file)
    sp15_file = open('results/sp15_' + timestr + '.csv','wb')
    sp15_writer = csv.writer(sp15_file)

    # REPEATEDLY PERFORM EXERCISE
    for k in range(2000):

        # GET NEW RANDOM PARAMTER DRAW
        cit_params, big_mov_params, lp, ip = new_rand_params(d, ds)
            
        # RUN COUNTERFACTUALS
        lo = big_mov_params[1]
        for lo_cf in [lo, 0.7 * lo, 0.5 * lo, 0.0 * lo]:
            print 'Current cost: %.2f' % (lo_cf)
            [cit_fracs, dep_fracs, dep_sds, dep_cfv] = offer_cf(lo_cf, cit_params,
                                                        big_mov_params,
                                                        lp, init, ip,
                                                        dep_stats, bd,
                                                        aut_pan, mov_dat91,
                                                        mov_dat_not91, qp)
            if lo_cf == lo:
                sp0_writer.writerow(cit_fracs + dep_fracs + dep_sds + dep_cfv)
                sp0_file.flush()
            if lo_cf == 0.7 * lo:
                sp05_writer.writerow(cit_fracs + dep_fracs + dep_sds + dep_cfv)
                sp05_file.flush()
            if lo_cf == 0.5 * lo:
                sp10_writer.writerow(cit_fracs + dep_fracs + dep_sds + dep_cfv)
                sp10_file.flush()
            if lo_cf == 0.0 * lo:
                sp15_writer.writerow(cit_fracs + dep_fracs + dep_sds + dep_cfv)
                sp15_file.flush()
        print k

run_cf()
