import pandas as pd
import matplotlib.pyplot as plt
import math
from scipy.stats import norm

#READ IN DATA
p = pd.read_csv('out.csv')

# EASIER TO DO LOGGING HERE
# p[' p'] = p[' p'].apply(lambda x: math.log(x))
p[' ip'] = p[' ip'].apply(lambda x: math.log(x))

def mkplt(x, sp1, sp2, sp3, y_name, ytop=0, log=False, ppf=False):
    if log:
        x = x.apply(lambda x: math.log(x))
    if ppf:
        x = x.apply(lambda x: norm.ppf(x))
    ax = plt.subplot(sp1, sp2, sp3)
    plt.plot(x, '-b', linewidth=0.5)
    plt.title(y_name, fontsize=10)
    ax.xaxis.set_major_formatter( plt.NullFormatter() )
    ax.yaxis.set_major_formatter( plt.NullFormatter() )
    if ytop != 0:
        plt.ylim([ytop[0],ytop[1]])
    return ax

fig1 = plt.figure(figsize=(17,  8),  dpi=80)
mkplt(p[' bet'],                3, 4, 1, 'bet', 0)
mkplt(p['alp'],                 3, 4, 2, 'alp', 0)
mkplt(p[' gam0'],               3, 4, 3, 'gam0', 0)
mkplt(p[' gam1'],               3, 4, 4, 'gam1', 0)
mkplt(p[' field_co'],           3, 4, 5, 'field_co'  , 0)
mkplt(p[' qual_co'],            3, 4, 6, 'qual_co'   , 0)
mkplt(p[' lat_co'],             3, 4, 7, 'lat_co'    , 0)
mkplt(p[' lo'],                 3, 4, 8, 'lo1'       , 0)
mkplt(p[' ip'],                 3, 4, 9, 'ip'        , 0)
mkplt(p[' lat_prob1'][::8],     3, 4, 10, 'lat_prob1' , 0)
mkplt(p[' lat_prob2'][::8],     3, 4, 11, 'lat_prob2' , 0)
mkplt(p[' lat_prob3'][::8],     3, 4, 12, 'lat_prob3' , 0)
plt.savefig('params_plots_bit.png', bbox_inches=0)

plt.show()
