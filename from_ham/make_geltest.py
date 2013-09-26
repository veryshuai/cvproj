# This script evaluates the gelman convergence criterion for a variety of
# parameters

import pandas as pd
import os
import glob
import math
from scipy.stats import norm


def load_dat(name, col_no, log=False, ppf=False):
    liks, mliks = [], []
    min_n, max_n = 1e6, 0
    k = 0
    for infile in glob.glob(os.path.join('', name)):
        new = pd.read_csv(infile).iloc[:, col_no]
        if log:
            new = new.apply(lambda x: math.log(x))
        if ppf:
            new = new.apply(lambda x: norm.ppf(x))
        mid = round(new.count() / 2)
        mid = 0
        liks.append(new[mid:])
        mliks.append(liks[k].describe().loc['mean'])
        min_n = min(liks[k].count(), min_n)
        max_n = max(liks[k].count(), max_n)
        k += 1
    return liks, mliks, min_n, max_n


def make_W(liks, mliks):
    var = []
    for l in liks:
        var.append(l.describe().loc['std'] ** 2)
    mean = sum(var) / len(var)
    return mean


def make_B(mliks, min_n, max_n):
    big_mean = sum(mliks) / len(mliks)
    s = 0
    for l in mliks:
        s += (l - big_mean) ** 2
    var_max = max_n * s / (len(mliks) - 1)
    var_min = min_n * s / (len(mliks) - 1)
    return var_max, var_min


def make_gels(name, col_no, params=False):
    liks, mliks, min_n, max_n = load_dat(name, col_no)
    if col_no in [10,13] and params:
        liks, mliks, min_n, max_n = load_dat(name, col_no, True)
    # if col_no in [2,3,9] and params:
    #     liks, mliks, min_n, max_n = load_dat(name, col_no, False, True)
    W = make_W(liks, mliks)
    B_max, B_min = make_B(mliks, min_n, max_n)
    var_max = (max_n - 1) / float(max_n) * W + 1 / float(max_n) * B_max
    var_min = (min_n - 1) / float(min_n) * W + 1 / float(min_n) * B_min
    R_max = math.sqrt(var_max / W)
    R_min = math.sqrt(var_min / W)
    print R_max
    return R_max

under = 0
total = 0
for k in range(15):
    R = make_gels('out_2*', k, True)
    if R:
        total += 1
        if R < 1.1:
            under += 1

print ''.join([ str(int(round(under / float(total) * 100))), '% passed the Gelman-Rubin test.'])
