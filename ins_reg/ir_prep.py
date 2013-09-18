# This script puts movement data in a stat compatible format

import pandas as pd

dat = pd.read_pickle('mov_dat.pickle')
bd  = pd.read_pickle('budget_def.pickle')
bd  = pd.DataFrame(bd).reset_index()
bd.columns = ['dep','bd']
dat = pd.merge(dat, bd, how='left')\
        .fillna(value=0)

dat.to_csv('mov_dat.csv')
