import pandas as pd
import matplotlib.pyplot as plt
import math
from scipy.stats import norm

#READ IN DATA
p = pd.read_csv('out.csv')

# EASIER TO DO LOGGING HERE
# p[' p'] = p[' p'].apply(lambda x: math.log(x))
p[' ip'] = p[' ip'].apply(lambda x: math.log(max(x,1e-12)))

def mkplt(x, sp1, sp2, sp3, y_name, ytop=0, log=False, ppf=False):
    if log:
        x = x.apply(lambda x: math.log(x))
    if ppf:
        x = x.apply(lambda x: norm.ppf(x))
    ax = plt.subplot(sp1, sp2, sp3)
    plt.plot(x, '-b', linewidth=0.5)
    plt.title(y_name, fontsize=10)
    ax.xaxis.set_major_formatter( plt.NullFormatter() )
    #ax.yaxis.set_major_formatter( plt.NullFormatter() )
    if ytop != 0:
        plt.ylim([ytop[0],ytop[1]])
    return ax

fig1 = plt.figure(figsize=(17,  8),  dpi=80)
mkplt(p[' bet0'],               4, 4, 1, 'bet0', 0)
mkplt(p[' bet1'],               4, 4, 2, 'bet1', 0)
mkplt(p['alp0'],                4, 4, 3, 'alp0', 0)
mkplt(p[' alp1'],               4, 4, 4, 'alp1', 0)
mkplt(p[' gam0'],               4, 4, 5, 'gam0', 0)
mkplt(p[' gam1'],               4, 4, 6, 'gam1', 0)
mkplt(p[' field_co'],           4, 4, 7, 'field_co'  , 0)
mkplt(p[' qual_co'],            4, 4, 8, 'qual_co'   , 0)
mkplt(p[' lat_co'],             4, 4, 9, 'lat_co'    , 0)
mkplt(p[' lo'],                 4, 4, 10, 'lo1'       , 0)
mkplt(p[' ip'],                 4, 4, 11, 'ip'        , 0)
mkplt(p[' lat_prob1'][::8],     4, 4, 12, 'lat_prob1' , 0)
mkplt(p[' lat_prob2'][::8],     4, 4, 13, 'lat_prob2' , 0)
mkplt(p[' lat_prob3'][::8],     4, 4, 14, 'lat_prob3' , 0)
plt.savefig('params_plots_big.png', bbox_inches=0)

plt.show()
