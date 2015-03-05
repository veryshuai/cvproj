import pandas as pd
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt

#READ IN DATA
reg = pd.read_csv('out_reg.csv')
split = pd.read_csv('out_split.csv')

def mkplt(x,sp1,sp2,sp3,y_name,ytop,col,lincol,zero_one=False,auto=True,x_min=0,x_max=1):
    ax = plt.subplot(sp1,sp2,sp3)
    if zero_one:
        xgrid = np.linspace(0, 1, 400)
    else:
        if auto:
            xgrid = np.linspace(x.min(), x.max(), 400)
        else:
            xgrid = np.linspace(x_min, x_max, 400)
            x = x[(x < x_max) & (x > x_min)]
    density = stats.kde.gaussian_kde(x)
    density.covariance_factor=lambda : 0.35
    density._compute_covariance()
    plt.hist(x, bins=20, normed=True, histtype='stepfilled', alpha=0.05, color=col)
    plt.plot(xgrid, density(xgrid), lincol, linewidth=2)
    if ytop != 0:
        plt.ylim([0,ytop])
    plt.ylabel(y_name,fontsize=12)
    plt.locator_params(nbins=4) # limits the number of x-axis points
    ax.yaxis.set_major_formatter( plt.NullFormatter() )

fig1 = plt.figure(figsize=(17, 8), dpi=80)
mkplt(split['alp0']    ,3,4,3,r'base param $\alpha_{NF}$'        ,0,'b','-r',False)
mkplt(split[' alp1']   ,3,4,4,r'base param $\alpha_{F}$'         ,0,'b','-r',False)
mkplt(split[' gam0']   ,3,4,11,r'interest prob $\gamma_{NF}$'    ,0,'b','-r',False)
mkplt(split[' gam1']   ,3,4,12,r'interest prob $\gamma_{F}$'     ,0,'b','-r',False)
mkplt(split[' bet0']   ,3,4,7,r'depend param $\beta_{NF}$'       ,0,'b','-r',False)
mkplt(split[' bet1']   ,3,4,8,r'depend param $\beta_{F}$'        ,0,'b','-r',False)
mkplt(reg['alp']       ,3,4,1,r'base param $\alpha$'             ,0,'y','-b',False)
mkplt(reg[' gam0']     ,3,4,9,r'interest prob $\gamma_{NF}$'     ,0,'y','-b',False)
mkplt(reg[' gam1']     ,3,4,10,r'interest prob $\gamma_{F}$'     ,0,'y','-b',False)
mkplt(reg[' bet0']     ,3,4,5,r'depend param $\beta_{dep}$'      ,0,'y','-b',False)
mkplt(reg[' bet1']     ,3,4,6,r'depend param $\beta_{reg}$'      ,0,'y','-b',False)
plt.savefig('params_dists_alt_models.png',bbox_inches=0)

plt.show()
