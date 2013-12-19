# This script runs some data cuts which give information for the prior I use

import datetime as dt
import pandas as pd
import numpy as np
import random as rand
import pickle
from time import clock, time
from copy import deepcopy
import re
from fuzzywuzzy import fuzz
import collections

#From stefan at stack overflow:
#http://stackoverflow.com/questions/3009935/looking-for-a-good-python-tree-data-structure
def tree():
    return collections.defaultdict(tree)

first_yr = 1986
last_yr = 2012

# LOAD FIRST CITATION TIMES AND TOTAL CITES
cit_times_df = pd.read_csv('cit_times.csv')
cit_times = list(cit_times_df['datetime'])
cit_times = [pd.Timestamp(x) for x in cit_times]
cit_times_df['cit_times'] = pd.Series(cit_times)
cit_times_df['au'] = cit_times_df['aut']
cit_times_df = cit_times_df[['au','cit_times','tot_cits']]
cit_times_df['cit_times'] = cit_times_df['cit_times'].apply(lambda x: x.year)
cit_times_df = cit_times_df[cit_times_df['cit_times'] <= last_yr]

# LOAD MAIN AUTHOR PANEL
aut_pan                     = pd.read_csv('authorpanel_final.csv')
aut_pan                     = aut_pan[pd.notnull(aut_pan['date'])] #remove NaN's
start_times                 = aut_pan.groupby('au')['date'].transform(lambda x: x.iloc[0])
end_times                   = aut_pan.groupby('au')['date'].transform(lambda x: x.iloc[-1])
start_times                 = start_times.apply(lambda x: int(x)-1)
end_times                   = end_times.apply(lambda x: int(x))
aut_pan['start_times']      = start_times
aut_pan['end_times']        = end_times
aut_pan = aut_pan[(aut_pan['date'] <= last_yr)
                  & (aut_pan['date'] >= first_yr)]

# DEAL WITH INCONSISTENCIES IN FIRST CITE TIME AND PANEL
combined_init                 = pd.merge(aut_pan,cit_times_df,on='au',how='left') #outer keeps the majority non-citers
combined                      = combined_init.sort('start_times').groupby('au').first()
combined_nonulls              = combined[pd.notnull(combined['cit_times'])]

# OPTION 1: EXTEND LIVES TO INCLUDE NON-CONFORMING FIRST CITE TIMES
# extend end_time if there is a later cite
extend_me = combined_nonulls['end_times'] < combined_nonulls['cit_times']
combined_extend_me = combined_nonulls.ix[extend_me]
combined_extend_me['end_times']                 = combined_extend_me['cit_times'].apply(lambda x: int(x))
combined_nonulls['end_times'].ix[extend_me]     = combined_extend_me['end_times']

# extend start_time if there is an earlier cite
extend_me              = combined_nonulls['start_times'] > combined_nonulls['cit_times']
combined_extend_me     = combined_nonulls.ix[extend_me]
combined_extend_me['start_times'] = combined_extend_me['cit_times'].apply(lambda x: int(x))
combined_nonulls['start_times'].ix[extend_me] = combined_extend_me['start_times']

# OPTION 2: DROP NON-CONFORMING CITES
# drop_me1                                            = combined_nonulls['end_times'] < combined_nonulls['cit_times']
# drop_me2                                            = combined_nonulls['start_times'] > combined_nonulls['cit_times']
# combined_nonulls['cit_times'][drop_me1]             = np.nan
# combined_nonulls['cit_times'][drop_me2]             = np.nan

# READ BACK INTO COMBINED
combined['start_times'][pd.notnull(combined['cit_times'])] = combined_nonulls['start_times']
combined['end_times'][pd.notnull(combined['cit_times'])] = combined_nonulls['end_times']
combined['isCiter']     = pd.notnull(combined['cit_times'])*1

# APPEND ONTO AUT_PAN
aut_pan  = aut_pan.reset_index().append(combined.reset_index()).sort_index(by = ['au','date'])
aut_pan  = aut_pan[['au','date','dep','start_times','end_times','cit_times','tot_cits','isCiter']].set_index('au')
fillcols = aut_pan.reset_index().sort_index(by = 'date').groupby('au').fillna(method = 'pad')
aut_pan  = fillcols.set_index('au')
aut_pan['isCiter'] = aut_pan['isCiter'].fillna(value=0)
fillcols = aut_pan.reset_index().groupby('au').fillna(method = 'bfill')
aut_pan  = fillcols.set_index(['au'])
aut_pan  = aut_pan.reset_index().drop_duplicates(cols = ['au','date'],take_last = False)

# FIX ISCITER
aut_pan['isCiter'][aut_pan['cit_times'] <= aut_pan['date']] = 1
aut_pan['isCiter'][aut_pan['cit_times'] > aut_pan['date']] = 0
aut_pan  = aut_pan.set_index(['au','date'])

# GET AUTHOR FIELDS (currently for Jensen)
fields          = pd.read_csv('collapsed.csv')
ecm             = fields.ix[list(fields[' NEP-CTA ']) == 1 or list(fields[' NEP-BEC '] == 1)]
drop_cols       = list(ecm.columns)
drop_cols.remove(' NAME ')
ecm             = ecm.drop(drop_cols,axis=1)
ecm             = pd.Series(list(ecm[' NAME '])).apply(lambda x: x.upper())
scan            = re.compile('([\p{L}\p{M}a-zA-z ]*,..)') #only first initial
ecm             = ecm.apply(lambda x: scan.match(x.strip()).group(1) if (type(x) == type(ecm[0]) and scan.match(x.strip()) != None) else x )

# MATCH FIELD TO AUTHOR PANEL, AND ADD INITIAL LATENT DRAWS
def on_the_list(x):
    max_rat = 0 #match score
    if type(x) == str:
        rating  = list(ecm[ecm == x])
        if rating == []:
            return 0
        else:
            return 1
    else:
        print 'WARNING: non-string in on_the_list function'
        return 0

aut_pan = aut_pan.reset_index()
aut_pan['au']       = aut_pan['au'].str.upper()
isField             = pd.DataFrame(aut_pan.groupby('au').first().reset_index())
isField['isField']  = aut_pan.groupby('au').first().reset_index()['au'].apply(lambda x: on_the_list(x))
aut_pan             = aut_pan.set_index('au').join(isField.drop('dep',axis=1).set_index('au'),how='outer',rsuffix='_r')
print aut_pan.reset_index().groupby('au').first()['isField'].value_counts()

aut_pan      = aut_pan[(pd.notnull(aut_pan.date)) & (aut_pan.date >= first_yr) & (aut_pan.date <= last_yr)]

# DISCRETIZE AND MATCH QUALITY TO AUTHOR PANEL
qual_list           = pd.read_csv('stata_usonly_qual_bar.csv',delimiter = '|').set_index('au')
quant               = pd.qcut(qual_list['qual'], [0, 0.33, 0.66, 1])
junk, quant_id      = np.unique(quant, return_inverse = True)
qual_list['qual']   = - (quant_id - 2)
aut_pan             = aut_pan.join(qual_list).reset_index()
aut_pan['dep_qual'] = aut_pan.groupby('dep')['qual'].transform(lambda x: x.mean())
aut_pan             = aut_pan.set_index('au')

# GET FIELD FRACTIONS
def field_frac(autpan,location,newvar):
    autpan         = autpan.reset_index()
    transformed    = autpan.groupby(location)['isField'].transform(lambda x: x.mean())
    autpan[newvar] = transformed
    return autpan
aut_pan      = field_frac(aut_pan,'dep','dmean')

# GET KNOW FRACTIONS
def know_frac(autpan,location,newvar):
    autpan         = autpan.reset_index()
    transformed    = autpan.groupby([location,'date'])['isCiter']\
            .transform(lambda x: sum(x*1) / max(float(len(x*1)) - 1,float(1)))
    autpan[newvar] = transformed
    return autpan
aut_pan      = know_frac(aut_pan,'dep','kfrac')

# PIVOT KNOW FRACTIONS
dep_years = aut_pan[['dep','date','kfrac']].drop_duplicates()
dep_years = dep_years.pivot(index='dep',columns='date',values='kfrac').fillna(value=0)

# CLEAN UP AUTPAN
aut_pan           = aut_pan[['au', 'date', 'dep', 'dmean', 'qual', 'dep_qual', 'kfrac', 'isField',
                             'start_times', 'end_times', 'cit_times',
                             'tot_cits', 'isCiter']].reset_index()
aut_pan['isMove'] = False

# SAVE CIT LIK STUFF
aut_pan = aut_pan[(aut_pan['date'] > first_yr) & (aut_pan['date'] <= last_yr)]
aut_pan = aut_pan[(aut_pan['start_times'] < 1995) & (aut_pan['end_times'] > 1986)]
first_deps = aut_pan.sort_index(by='date')\
            .groupby('au').first().reset_index()
first_ff = first_deps.set_index('au')[['dmean', 'isField']]
first_cits = aut_pan[aut_pan['isCiter'] == 1].sort_index(by='date')\
             .groupby('au').first().reset_index()
ever_cit = aut_pan[aut_pan['isField'] == 1].groupby('au')['isCiter']\
        .apply(lambda x: max(x)).value_counts()
print ever_cit
ever_cit = aut_pan[aut_pan['isField'] == 0].groupby('au')['isCiter']\
        .apply(lambda x: max(x)).value_counts()
print ever_cit

# Field Jensen ever citers, around before 1994
#0    112
#1     45
# Not Field Jensen ever citers, around before 1994
#0    3866
#1     240
