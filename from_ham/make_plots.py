import pandas as pd
import matplotlib.pyplot as plt
import math
from scipy.stats import norm

#READ IN DATA
p = pd.read_csv('out.csv')


def mkplt(x, sp1, sp2, sp3, y_name, ytop=0, log=False, ppf=False):
    if log:
        x = x.apply(lambda x: math.log(x))
    if ppf:
        x = x.apply(lambda x: norm.ppf(x))
    ax = plt.subplot(sp1, sp2, sp3)
    plt.plot(x, '-b', linewidth=0.5)
    plt.ylabel(y_name, fontsize=10)
    #ax.yaxis.set_major_formatter( plt.NullFormatter() )
    if ytop != 0:
        plt.ylim([0,ytop])
    return ax

fig1 = plt.figure(figsize=(17,  8),  dpi=80)
mkplt(p[' bet'], 2, 2, 1, 'bet', 0)
mkplt(p['alp'],  2, 2, 2, 'alp', 0)
mkplt(p[' gam0'], 2, 2, 3, 'gam0', 0)
mkplt(p[' gam1'], 2, 2, 4, 'gam1', 0)
plt.savefig('params1_plots_lat.png', bbox_inches=0)

fig2 = plt.figure(figsize=(17,  8),  dpi=80)
mkplt(p[' field_co'],     3, 3, 1, 'field_co'  , 0)
mkplt(p[' qual_co'],      3, 3, 2, 'qual_co'   , 0)
mkplt(p[' lat_co'],       3, 3, 3, 'lat_co'    , 0)
mkplt(p[' lo1'],          3, 3, 4, 'lo1'       , 0)
mkplt(p[' lo2'],          3, 3, 5, 'lo2'       , 0)
mkplt(p[' p'],            3, 3, 6, 'p'         , 0)
mkplt(p[' ip'],           3, 3, 8, 'ip'        , 0)
plt.savefig('params2_plots_lat.png', bbox_inches=0)

fig3 = plt.figure(figsize=(17, 8), dpi=80)
mkplt(p[' lat_prob1'],    3, 1, 1, 'lat_prob1' , 0)
mkplt(p[' lat_prob2'],    3, 1, 2, 'lat_prob2' , 0)
mkplt(p[' lat_prob3'],    3, 1, 3, 'lat_prob3' , 0)
plt.savefig('params3_plots_lat.png', bbox_inches=0)

plt.show()
