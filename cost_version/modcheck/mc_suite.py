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
    close_lat = int(np.argmin(difarray))

    return pd.Series([true_lat, close_lat])

def make_int(field, cp, name): 
    """ stochastically assigns interest """
    if name == 'base':
        ft = cp[0][1][0]
    if name == 'reg':
        ft = cp[0][1][0]
    if name == 'split':
        ft = cp[0][1][field]
    if random.random() < ft:
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

def u_cit(r, kf, nf, cp, yr, qp, name):
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
        print kf
        pkf = 0
        pnf = 0

    # GET CIT PROBS
    if name == 'split':
        alp = cp[2][0][r['isField'].iat[0]]
        bet = cp[2][2][r['isField'].iat[0]]
        arg = math.exp(alp + bet * pkf + qp[int(r['closelat'].iat[0])])
        prob = arg / (1 + arg)

    if name == 'reg':
        alp = cp[1][0][0]
        bet = cp[1][2][0]
        betr = cp[1][2][1]
        arg = math.exp(alp + bet * pkf + betr * pnf + qp[int(r['closelat'].iat[0])])
        prob = arg / (1 + arg)

    if name == 'base':
        alp = cp[0][0][0]
        bet = cp[0][2][0]
        arg = math.exp(alp + bet * pkf + qp[int(r['closelat'].iat[0])])
        prob = arg / (1 + arg)

    # U CITE BRO?
    if random.random() < prob:
        return 1
    else:
        return 0

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

    # ASSIGN LATENT TYPE AND INTEREST TO 1986 AUTHORS
    aut_pan = aut_pan[aut_pan['date'] == 1987]
    latcomb = aut_pan.apply(lambda row: make_lat(row, lp, qp), 
                             axis=1)
    aut_pan['truelat'] = latcomb[0]
    aut_pan['closelat'] = latcomb[1]
    aut_pan = aut_pan.reset_index()
    aut_pan['nat'] = 'USA'

    # SIMULATE MOVES BETWEEN DEPARTMENTS
    print 'WORKING ON MOVES'
    moves = aut_pan.groupby('au').apply(lambda x:
                                          make_moves(x, trans))\
                                 .reset_index()
    moves = pd.merge(moves, aut_pan, on='au')
    moves = moves[['au', 'level_1','dep_x', 'nat','isField','truelat','closelat']]
    moves.columns = ['au', 'year', 'dep', 'nat', 'isField', 'truelat','closelat']

    # CALCULATE TRUE MOVE PERCENTAGE
    moves['next_dep'] = moves.groupby('au')['dep'].apply(lambda x: x.shift(-1))
    non_moves = moves[moves['next_dep'] == moves['dep']]['next_dep'].count()
    tot_moves = moves['next_dep'].count()
    movfrac = 1 - non_moves / float(tot_moves)
    print 'Fraction of move years: %.2f' % (movfrac)

    # SIMULATE SPREAD OF KNOWLEDGE THROUGH DEPARTMENTS
    print 'NOW ON CITS'
    results = [] 
    for name in ['base','reg','split']:
        cit_evol = deepcopy(moves)
        cit_evol['citer'] = 0
        cit_fracs = []
        dep_fracs = []
        dep_sds   = []
        cit_evol['isInt'] = cit_evol['isField']\
                .apply(lambda x: make_int(x, cit_params, name))
        for year in range(int(cit_evol['year'].min()+1), int(cit_evol['year'].max()+1)):
            #knowledge fractions
            kf = cit_evol[cit_evol['year'] == year- 1].groupby('dep')['citer'].mean() 
            nf = cit_evol[cit_evol['year'] == year- 1].groupby('nat')['citer'].mean() 
            # get new cites
            cit_list = cit_evol.groupby('au')\
                                .apply(lambda r: u_cit(r, kf, nf, cit_params, year, qp, name))
            cit_evol = pd.merge(cit_evol, pd.DataFrame(cit_list).reset_index(), on='au')
            cit_evol['citer'] = cit_evol[0]
            cit_evol = cit_evol.drop(0, axis=1)
            cit_fracs.append(cit_evol.groupby('au')['citer'].max().describe()['mean'])
            dep_fracs.append(cit_evol[cit_evol['year'] == year].groupby('dep')['citer'].max().describe()['mean'])
            sds = cit_evol[cit_evol['year'] == year].groupby('dep')['citer'].mean().describe()['std']
            mean = cit_evol[cit_evol['year'] == year].groupby('dep')['citer'].mean().describe()['mean']
            dep_sds.append(sds / mean) # coefficient of variation
        results.append(cit_fracs + dep_fracs + dep_sds)

    return results 

def new_rand_params(d, ds):
    """ takes converged posterior and draws a random parameter vector"""

    cit_params = []
    # RANDOM PARAMETER VECTOR
    ch = d[0].iloc[random.randrange(ds[0])]
    cit_params.append([[ch['alp']], 
                  [ch[' gam0'], ch[' gam1']],
                  [ch[' bet']]])
    mov_params = pd.Series({'field':ch[' field_co'],
                            'lat': ch[' lat_co'],
                            'qual': ch[' qual_co']})
    big_mov_params = [mov_params, ch[' lo'],
                      ch[' p']]
    lp = [ch[' lat_prob1'],
          ch[' lat_prob2'],
          ch[' lat_prob3']]
    ip = ch[' ip']

    # REG PARAMS
    ch = d[1].iloc[random.randrange(ds[1])]
    cit_params.append([[ch['alp']], 
                  [ch[' gam0'], ch[' gam1']],
                  [ch[' bet0'],ch[' bet1']]])

    # SPLIT PARAMS
    ch = d[2].iloc[random.randrange(ds[2])]
    cit_params.append([[ch['alp0'], ch[' alp1']], 
                  [ch[' gam0'], ch[' gam1']],
                  [ch[' bet0'],ch[' bet1']]])
    return cit_params, big_mov_params, lp, ip


def run_cf():
    """ reads from a results file, and calls
        counterfactual generation program """

    # LOAD PARAMETERS
    db = pd.read_csv('out.csv')
    dbs = db.shape[0]
    dr = pd.read_csv('out_nat.csv')
    dsr = dr.shape[0]
    dsp = pd.read_csv('out_split.csv')
    dssp = dsp.shape[0]
    d = [db, dr, dsp]
    ds = [dbs, dsr, dssp]

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
    spb_file = open('results/spb_' + timestr + '.csv','wb')
    spb_writer = csv.writer(spb_file)
    spr_file = open('results/spr_' + timestr + '.csv','wb')
    spr_writer = csv.writer(spr_file)
    sps_file = open('results/sps_' + timestr + '.csv','wb')
    sps_writer = csv.writer(sps_file)

    # REPEATEDLY PERFORM EXERCISE
    for k in range(2000):

        # GET NEW RANDOM PARAMTER DRAW
        cit_params, big_mov_params, lp, ip = new_rand_params(d, ds)
            
        # RUN COUNTERFACTUALS
        lo = big_mov_params[1]
        results = offer_cf(lo, cit_params, big_mov_params, lp,
                             init, ip, dep_stats, bd, aut_pan,
                             mov_dat91, mov_dat_not91, qp)
        spb_writer.writerow(results[0])
        spb_file.flush()
        spr_writer.writerow(results[1])
        spr_file.flush()
        sps_writer.writerow(results[2])
        sps_file.flush()
        print k

run_cf()
