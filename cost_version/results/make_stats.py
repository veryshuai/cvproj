# Makes means and variances for parameter table

import pandas as pd

dat = pd.read_csv('out.csv')

dat.describe().T.to_csv('stats.csv')
