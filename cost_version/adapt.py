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
        col_names = ['alpha_0','alpha_1', 'alpha_2', 'alpha_3', 
                     'alpha_4','gam_0', 'gam_1',
                     'bet', 'field_co', 'lat_co',
                     'qual_co', 'lo','p',
                     'lp1', 'lp2', 'lp3', 'ip']
        if k < 1:
            dat = pd.read_csv('old_out.csv', header=None,
                    names=col_names)
        else:
            dat = pd.read_csv('results/out_' + snip + '.csv', header=None,
                    names=col_names)

        # keep only several thousand last iterations
        d = dat.shape[0]
        print d
        if d > 5000:
            dat = dat[-5000:]
            
        # CIT BLOCK
        if block_name == 'cit':
            citdat = dat[['alpha_0', 'alpha_1', 'alpha_2', 'alpha_3',
                'alpha_4','gam_0', 'gam_1', 'bet']]
            citdat.loc[:,'gam_0'] = citdat['gam_0'].apply(lambda x: norm.ppf(x, 0, 1))
            citdat.loc[:,'gam_1'] = citdat['gam_1'].apply(lambda x: norm.ppf(x, 0, 1))

            d = citdat.shape[1]
            if k % 4 + 1 < d:
                flag = True
            else:
                flag = False
            cit_cov = citdat.cov()
            if flag:
                cit_rnd = mvn(np.zeros(d), np.identity(d) * 0.0001 * s / float(d))
            else:
                cit_rnd = (1 - b) * mvn(np.zeros(d), cit_cov * s / float(d))\
                        + b * mvn(np.zeros(d), np.identity(d) * s / float(d))
            cit_rnd = pd.Series(cit_rnd, index=['alpha_0', 'alpha_1', 
                'alpha_2', 'alpha_3','alpha_4','gam_0', 'gam_1', 'bet'])
            loc_rnd = 0
        else:
            locdat = dat[['field_co', 'lat_co', 'qual_co',
                          'lo', 'p', 'ip']]
            # locdat['p'] = locdat['p'].apply(lambda x: math.log(x - 1))
            locdat.loc[:,'ip'] = locdat['ip'].apply(lambda x: math.log(x))

            d = locdat.shape[1] 
            if k % 4 + 1 < d:
                flag = True
            else:
                flag = False
            loc_cov = locdat.cov()
            if flag:
                loc_rnd = mvn(np.zeros(d), np.identity(d) * 0.0001 * s / float(d))
            else:
                loc_rnd = (1 - b) * mvn(np.zeros(d), loc_cov * s / float(d))\
                        + b * mvn(np.zeros(d), np.identity(d) * s / float(d))
            loc_rnd = pd.Series(loc_rnd, index=['field_co', 'lat_co', 'qual_co',
                                                'lo', 'p', 'ip'])
            cit_rnd = 0
    else:
        print 'ERROR: Invalid block name in adapt.py script'
        cit_rnd, loc_rnd = 0
    return [cit_rnd, loc_rnd]
