# This script makes stats for parameter table in extension section:

import pandas as pd

if __name__ == '__main__':
    """main"""
    
    # READ DATA 
    b = pd.read_csv('out.csv')
    r = pd.read_csv('out_reg.csv')
    s = pd.read_csv('out_split.csv')
    l = pd.read_csv('out_lag.csv')

    r.columns = ['alp', ' gam0', ' gam1', ' bet', ' bet_r', ' field_co', ' lat_co', ' qual_co', ' lo', ' p', ' lat_prob1', ' lat_prob2', ' lat_prob3', ' ip']
    s.columns = ['alp', ' alp_f', ' gam0', ' gam1', ' bet', ' bet_f', ' field_co', ' lat_co', ' qual_co', ' lo', ' p', ' lat_prob1', ' lat_prob2', ' lat_prob3', ' ip']

    # MAKE TABLE
    tab = pd.DataFrame({'baseline':     b.describe().loc['mean'],
                        'region':       r.describe().loc['mean'],
                        'field-spec':   s.describe().loc['mean'],
                        'lag':          l.describe().loc['mean']})
    tab.to_csv('stats_tab.csv')

    # MAKE SD
    tab = pd.DataFrame({'baseline':     b.describe().loc['std'],
                        'region':       r.describe().loc['std'],
                        'field-spec':   s.describe().loc['std'],
                        'lag':          l.describe().loc['std']})
    tab.to_csv('stats_sd.csv')

    
