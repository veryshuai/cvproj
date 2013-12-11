# This script gets the time of each authors first citation, as well as the total number of citations for each author.
# Tasks:
# 1. isolate citation author names and years
# 2. merge with panel list in pandas format, years as datetime objects
# 3. profit
# Manifest:
# GrossmanHart.csv #contains all the papers which cited Grossman Hart 1986
# autpan.p #pickled autpan list of authors, haven't settled on the exact file yet 

import pandas as pd
import pickle
import numpy as np
import datetime as dt
import re

# date parser adapted from http://www.yulebiao.com/questions/12269528/using-python-pandas-to-parse-csv-with-date-in-format-year-day-hour-min-sec
def parse(yr):
    if np.isnan(yr)==0:
        yr = int(yr)
        my_date = pd.Timestamp(dt.datetime(yr,1,1)) # academics cite papers on the first of the year
    else:
        my_date = pd.Timestamp(dt.datetime(1900,9,1))
    return my_date

# READ IN CITING PANEL
citmat = pd.read_csv('GrossmanHart.csv', parse_dates={'datetime':
           ['year']},
           date_parser=parse)#, index_col=['year'])

# remove excess columns
drop_cols = list(citmat.columns)
for keep_me in ['author1','author2','author3','author4','author5','author6','author7','author8','datetime']:
    drop_cols.remove(keep_me)
citmat = citmat.drop(drop_cols,axis=1)

# STACK BY AUTHOR
citmat_new = pd.DataFrame({'aut': citmat['author1'],'datetime': citmat['datetime']})
for k in range(2,9):
    temp = pd.DataFrame({'aut': citmat['author' + str(k)],'datetime': citmat['datetime']})
    citmat_new = citmat_new.append(temp[pd.notnull(temp['aut'])])

# PUT AUTHOR IN CORRECT FORMAT (ONE INITIAL, ALL CAPS)
citmat_new['aut'] = citmat_new['aut'].str.upper()
citmat_new        = citmat_new[pd.notnull(citmat_new['aut'])]
aut_list          = list(citmat_new['aut'])
def one_init(x):
    try:
        return re.match('(^.*,\ [A-Z])(.*)',x).group(1)
    except:
        print x
        return x
citmat_new['aut'] = pd.Series([one_init(x) for x in aut_list])
citmat_new        = citmat_new.sort(columns='datetime')

# GET TIME OF FIRST CITATION
cit_times = pd.DataFrame(citmat_new.groupby('aut')['datetime'].first())
cit_times['tot_cits'] = citmat_new.groupby('aut').size()

# FILTER BY AUTHORS IN MY DEPARTMENT PANEL
au_list = pickle.load(open('au_list.p','rb'))
cit_times = cit_times[cit_times.index.isin(au_list)] 

# WRITE TO CSV
cit_times.to_csv('cit_times.csv')

