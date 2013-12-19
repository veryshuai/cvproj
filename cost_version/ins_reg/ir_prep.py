# This script puts movement data in a stat compatible format

import pandas as pd

# FOR FIRST REGRESSION
dat = pd.read_pickle('mov_dat.pickle')
bd  = pd.read_pickle('budget_def.pickle')
bd  = pd.DataFrame(bd).reset_index()
bd.columns = ['dep','bd','isstate']
dat = pd.merge(dat, bd, how='left')\
        .fillna(value=0)

dat.to_csv('mov_dat.csv')

# FOR CIT REGRESSION
aut_pan = pd.read_pickle('initial_panel.pickle')
aut_pan = pd.merge(aut_pan, bd, how='left')
aut_pan['bd'] = aut_pan['bd'].fillna(value=0)

aut_pan.to_csv('aut_pan.csv')
