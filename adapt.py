# This script calculates the realized standard deviation of each parameter in
# the model for use in adaptive mcmc proposals

import pandas as pd
import numpy as np
from numpy.random import multivariate_normal as mvn
from scipy.stats import norm
import math

def get_cov(snip, k, block_name):
    if block_name == 'cit' or block_name == 'loc':
        b = 0.001  # small number
        s = 2.38 ** 2 # optimal scaling factor 
        col_names = ['alpha_0', 'alpha_1', 'gam_0', 'gam_1',
                     'bet_0', 'bet_1', 'field_co', 'lat_co',
                     'qual_co', 'lo', 'p', 'lp1', 'lp2', 'ip']
        dat = pd.read_csv('results/out_' + snip + '.csv', header=None,
                             names=col_names)
        # keep only thousand last iterations
        d = dat.shape[0]
        print d
        if d > 1000:
            dat = dat[-1000:]
            
        # CIT BLOCK
        if block_name == 'cit':
            citdat = dat[['alpha_0', 'alpha_1', 'gam_0', 'gam_1',
                     'bet_0', 'bet_1']]
            citdat['gam_0'] = citdat['gam_0'].apply(lambda x: norm.ppf(x, 0, 1))
            citdat['gam_1'] = citdat['gam_1'].apply(lambda x: norm.ppf(x, 0, 1))

            d = citdat.shape[1]
            if k % 4 + 1 < d:
                flag = True
            cit_cov = citdat.cov()
            if flag:
                cit_rnd = mvn(np.zeros(d), np.identity(d) * 0.01 * s / float(d))
            else:
                cit_rnd = (1 - b) * mvn(np.zeros(d), cit_cov * s / float(d))\
                        + b * mvn(np.zeros(d), np.identity(d) * 0.01 * s / float(d))
            cit_rnd = pd.Series(cit_rnd, index=['alpha_0', 'alpha_1', 'gam_0', 'gam_1',
                     'bet_0', 'bet_1'])
            print cit_rnd
            loc_rnd = 0
        else:
            locdat = dat[['field_co', 'lat_co', 'qual_co', 'lo', 'p', 'ip']]
            locdat['lo'] = locdat['lo'].apply(lambda x: norm.ppf(x, 0, 1))
            locdat['p'] = locdat['p'].apply(lambda x: math.log(x - 1))
            locdat['ip'] = locdat['ip'].apply(lambda x: math.log(x))

            d = locdat.shape[1] 
            if k % 4 + 1 < d:
                flag = True
            loc_cov = locdat.cov()
            if flag:
                loc_rnd = mvn(np.zeros(d), np.identity(d) * 0.01 * s / float(d))
            else:
                loc_rnd = (1 - b) * mvn(np.zeros(d), loc_cov * s / float(d))\
                        + b * mvn(np.zeros(d), np.identity(d) * 0.01 * s / float(d))
            loc_rnd = pd.Series(loc_rnd, index=['field_co', 'lat_co', 'qual_co',
                                                'lo', 'p', 'ip'])
            print loc_rnd
            cit_rnd = 0
    else:
        print 'ERROR: Invalid block name in adapt.py script'
        cit_rnd, loc_rnd = 0
    return [cit_rnd, loc_rnd]
