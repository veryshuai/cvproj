import pandas as pd
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
import math

#READ IN DATA
params = pd.read_csv('out.csv')

# EASIER TO DO LOGGING HERE
print params[' p'].describe()
print params[' ip'].describe()
# params[' p'] = params[' p'].apply(lambda x: math.log(x))
params[' ip'] = params[' ip'].apply(lambda x: math.log(x))

def mkplt(x,sp1,sp2,sp3,y_name,ytop,zero_one=False,auto=True,x_min=0,x_max=1):
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
    plt.hist(x, bins=20, normed=True, histtype='stepfilled', alpha=0.05)
    plt.plot(xgrid, density(xgrid), '-r', linewidth=2)
    if ytop != 0:
        plt.ylim([0,ytop])
    plt.ylabel(y_name,fontsize=18)
    plt.locator_params(nbins=4)
    ax.yaxis.set_major_formatter( plt.NullFormatter() )

def mkplt2(x,z,lab1='',lab2='',sp1=1,sp2=1,sp3=1,ytop=0,zero_one='True'):
    ax = plt.subplot(sp1,sp2,sp3)
    density = stats.kde.gaussian_kde(x)
    if zero_one:
        xgrid = np.linspace(0, 1, 400)
    else:
        xgrid = np.linspace(x.min(), x.max(), 400)
    density.covariance_factor=lambda : 0.35
    density._compute_covariance()
    plt.hist(x, bins=20, normed=True, histtype='stepfilled', alpha=0.5,color='b',label=lab1)
    plt.hist(z, bins=20, normed=True, histtype='stepfilled', alpha=0.5,color='r',label=lab2)
    if ytop != 0:
        plt.ylim([0,ytop])
    ax.yaxis.set_major_formatter( plt.NullFormatter() )

fig1 = plt.figure(figsize=(17, 8), dpi=80)
mkplt(params['alp']         ,3,4,1,r'base learn prob $\alpha$'       ,0,False)
mkplt(params[' gam0']       ,3,4,2,r'interest prob $\gamma_{NF}$'      ,0,False)
mkplt(params[' gam1']       ,3,4,3,r'interest prob $\gamma_{F}$'    ,0,False)
mkplt(params[' bet0']       ,3,4,4,r'depend learn prob $\beta_0$'     ,0,False)
mkplt(params[' bet1']       ,3,4,5,r'region learn prob $\beta_1$'     ,0,False)
mkplt(params[' field_co']   ,3,4,6,r'field wage $\xi_f$'  ,0,False)
mkplt(params[' lat_co']     ,3,4,7,r'lat wage $\xi_l$'  ,0,False)
mkplt(params[' qual_co']    ,3,4,8,r'qual wage $\xi_q$' ,0,False)
mkplt(params[' lo']         ,3,4,9,r'offer arrival $\lambda_o$'     ,0,False)
mkplt(params[' lat_prob2']  ,3,4,10,r'init_cond $\phi_F$'  ,0,False)
mkplt(params[' lat_prob3']  ,3,4,11,r'lat disp $\sigma$'   ,0,False)
mkplt(params[' ip']         ,3,4,12,r'log exog $\xi_{ex}$' ,0,False)
plt.savefig('params_dists_reg.png',bbox_inches=0)
plt.show()

