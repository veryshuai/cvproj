import pandas as pd
import matplotlib.pyplot as plt
import math
from scipy.stats import norm

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

if __name__ == '__main__':

    #READ IN DATA
    p = pd.read_csv('out.csv')
    import pdb; pdb.set_trace()
    
    # EASIER TO DO LOGGING HERE
    # p[' p'] = p[' p'].apply(lambda x: math.log(x))
    #p[' ip'] = p[' ip'].apply(lambda x: math.log(x))
    
    fig1 = plt.figure(figsize=(17,  8),  dpi=80)
    mkplt(p[' bet'],                7, 2, 1, 'bet', 0)
    mkplt(p['alp0'],                7, 2, 2, 'alp0', 0)
    mkplt(p[' alp1'],               7, 2, 3, 'alp1', 0)
    mkplt(p[' gam0'],               7, 2, 4, 'gam0', 0)
    mkplt(p[' gam1'],               7, 2, 5, 'gam1', 0)
    mkplt(p[' field_co'],           7, 2, 6, 'field_co'  , 0)
    mkplt(p[' qual_co'],            7, 2, 7, 'qual_co'   , 0)
    mkplt(p[' lat_co'],             7, 2, 8, 'lat_co'    , 0)
    mkplt(p[' lo'],                 7, 2, 9, 'lo1'       , 0)
    mkplt(p[' ip'],                 7, 2, 10, 'ip'        , 0)
    mkplt(p[' lat_prob1'][::8],     7, 2, 11, 'lat_prob1' , 0)
    mkplt(p[' lat_prob2'][::8],     7, 2, 12, 'lat_prob2' , 0)
    mkplt(p[' lat_prob3'][::8],     7, 2, 13, 'lat_prob3' , 0)
    plt.savefig('params_plots_big.png', bbox_inches=0)
    
    plt.show()
