import pandas as pd
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
import math

#READ IN DTA
params = pd.read_csv('out.csv')
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
mkplt(params['alp']         ,3,4,1,r'base learn $\alpha$'       ,0,False)
mkplt(params[' bet']        ,3,4,4,r'depend learn $\beta$'     ,0,False)
mkplt(params[' gam0']       ,3,4,2,r'interest prob $\gamma_{NF}$'      ,0,False)
mkplt(params[' gam1']       ,3,4,3,r'interest prob $\gamma_{F}$'    ,0,False)
mkplt(params[' field_co']   ,3,4,5,r'field wage $\xi_f$'  ,0,False)
mkplt(params[' lat_co']     ,3,4,6,r'lat wage $\xi_l$'    ,0,False)
mkplt(params[' qual_co']    ,3,4,7,r'qual wage $\xi_q$'   ,0,False)
mkplt(params[' lo']         ,3,4,8,r'offer arrival $\lambda_o$'     ,0,False)
# mkplt(params[' lat_prob1']  ,3,4,9,r'init_cond base'   ,0,False)
mkplt(params[' lat_prob2']  ,3,4,9, r'init_cond $\phi_F$'   ,0,False)
mkplt(params[' lat_prob3']  ,3,4,10,r'lat disp $\sigma$'   ,0,False)
mkplt(params[' ip']         ,3,4,11,r'log exog $\xi_{ex}$'     ,0,False)
plt.savefig('params_dists_lag.png',bbox_inches=0)
# fig2 = plt.figure(
# mkplt(et_calc['i0'],221,r'$i_0$')
# mkplt(et_calc['i1'],222,r'$i_1$')
# mkplt(et_calc['s0'],223,r'$s_0$')
# mkplt(et_calc['s1'],224,r'$s_1$')
# plt.savefig('et_calc_dists.png',bbox_inches=0)
# fig3 = plt.figure()
# mkplt(liks['l'],111,r'$liks$')
# plt.savefig('lik_dists.png',bbox_inches=0)
# fig4 = plt.figure()
# mkplt(know_fracs0['ut']  ,3,2,1,r'us0'    ,0,True)
# mkplt(know_fracs0['ft']  ,3,2,2,r'for0'   ,10,True)
# mkplt(know_fracs1['ut']  ,3,2,3,r'us1'    ,0,True)
# mkplt(know_fracs1['ft']  ,3,2,4,r'for1'   ,10,True)
# mkplt(know_fracs2['ut']  ,3,2,5,r'us2'    ,0,True)
# mkplt(know_fracs2['ft']  ,3,2,6,r'for2'   ,10,True)
# mkplt(know_fracs0['wt']  ,421,r'world$'  )
# mkplt(know_fracs0['ut']  ,423,r'us'  )
# mkplt(know_fracs0['cat'] ,425,r'canada'  )
# mkplt(know_fracs0['et']  ,427,r'england'  )
# mkplt(know_fracs0['it']  ,422,r'israel')
# mkplt(know_fracs0['at']  ,424,r'australia')
# mkplt(know_fracs0['cht'] ,426,r'china')
# mkplt(know_fracs0['wsf'] ,428,r'world_field')
# fig5 = plt.figure()
# mkplt(know_fracs1['wt']  ,421,r'world$'  )
# mkplt(know_fracs1['ut']  ,423,r'us'  )
# mkplt(know_fracs1['cat'] ,425,r'canada'  )
# mkplt(know_fracs1['et']  ,427,r'england'  )
# mkplt(know_fracs1['it']  ,422,r'israel')
# mkplt(know_fracs1['at']  ,424,r'australia')
# mkplt(know_fracs1['cht'] ,426,r'china')
# mkplt(know_fracs1['wsf'] ,428,r'world_field')
# fig6 = plt.figure()
# mkplt(know_fracs2['wt']  ,421,r'world$'  )
# mkplt(know_fracs2['ut']  ,423,r'us'  )
# mkplt(know_fracs2['cat'] ,425,r'canada'  )
# mkplt(know_fracs2['et']  ,427,r'england'  )
# mkplt(know_fracs2['it']  ,422,r'israel')
# mkplt(know_fracs2['at']  ,424,r'australia')
# mkplt(know_fracs2['cht'] ,426,r'china')
# mkplt(know_fracs2['wsf'] ,428,r'world_field')
# plt.savefig('know_fracs2_dists.png',bbox_inches=0)
# plt.savefig('know_fracs_dists_world.png',bbox_inches=0)
# fig5 = plt.figure()
# mkplt2(know_fracs0['ft'],know_fracs1['ft'],'0','2')
plt.show()
