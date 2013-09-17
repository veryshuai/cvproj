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
# mkplt(p['alp_q0_f0_l0'],  3, 4, 1, 'alp_q0_f0_l0', 0)
# mkplt(p[' alp_q0_f1_l0'], 3, 4, 2, 'alp_q0_f1_l0', 0)
# mkplt(p[' alp_q1_f0_l0'], 3, 4, 3, 'alp_q1_f0_l0', 0)
# mkplt(p[' alp_q1_f1_l0'], 3, 4, 4, 'alp_q1_f1_l0', 0)
# mkplt(p[' alp_q2_f0_l0'], 3, 4, 5, 'alp_q2_f0_l0', 0)
# mkplt(p[' alp_q2_f1_l0'], 3, 4, 6, 'alp_q2_f1_l0', 0)
# mkplt(p[' gam_q0_f0_l0'], 3, 4, 7, 'gam_q0_f0_l0', 0)
# mkplt(p[' gam_q0_f1_l0'], 3, 4, 8, 'gam_q0_f1_l0', 0)
# mkplt(p[' gam_q1_f0_l0'], 3, 4, 9, 'gam_q1_f0_l0', 0)
# mkplt(p[' gam_q1_f1_l0'], 3, 4, 10, 'gam_q1_f1_l0', 0)
# mkplt(p[' gam_q2_f0_l0'], 3, 4, 11, 'gam_q2_f0_l0', 0)
# mkplt(p[' gam_q2_f1_l0'], 3, 4, 12, 'gam_q2_f1_l0', 0)
plt.savefig('params1_plots_lat.png', bbox_inches=0)

fig2 = plt.figure(figsize=(17,  8),  dpi=80)
mkplt(p[' field_co'],     3, 3, 7, 'field_co' , 0)
# mkplt(p[' qual_co'],    3, 3, 8, 'qual_co'  , 0)
mkplt(p[' lo'],           3, 3, 8, 'lo'       , 0)
mkplt(p[' p'],            3, 3, 9, 'p'        , 0)
mkplt(p[' bet_q0_f0_l0'], 3, 3, 3, 'bet_q0_f0_l0', 0)
mkplt(p[' bet_q0_f1_l0'], 3, 3, 6, 'bet_q0_f1_l0', 0)
mkplt(p['alp_q0_f0_l0'],  3, 3, 1, 'alp_q0_f0_l0', 0)
mkplt(p[' alp_q0_f1_l0'], 3, 3, 4, 'alp_q0_f1_l0', 0)
mkplt(p[' gam_q0_f0_l0'], 3, 3, 2, 'gam_q0_f0_l0', 0)
mkplt(p[' gam_q0_f1_l0'], 3, 3, 5, 'gam_q0_f1_l0', 0)
plt.savefig('params2_plots_lat.png', bbox_inches=0)

plt.show()