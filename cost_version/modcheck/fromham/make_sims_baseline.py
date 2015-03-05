# This script plots simulations for baseline vs the data

import pandas as pd
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
import math

#READ IN DATA
spreadb          = pd.read_csv('spreadb.csv')
spreadr          = pd.read_csv('spreadr.csv')
spreads          = pd.read_csv('spreads.csv')
spreadl          = pd.read_csv('spreadl.csv')

def mkplt(x,sp1,sp2,sp3,y_name,col='-b',inc_dat=False,tot=False):
    ax = plt.subplot(sp1,sp2,sp3)
    xgrid = [1987,1988,1989,1990,1991,1992, 1993]
    means = []
    five = []
    twentyfive = []
    seventyfive = []
    ninetyfive = []
    stderr = []
    meds = []
    for name in x.columns:
        des = x[name].describe()
        means.append(des['mean'])
        twentyfive.append(x[name].quantile(q=0.025))
        seventyfive.append(x[name].quantile(q=0.975))
        five.append(x[name].quantile(q=0.0005))
        ninetyfive.append(x[name].quantile(q=0.995))
        meds.append(x[name].quantile(q=0.5))
        stderr.append(1.65 * des['std'] / math.sqrt(x[name].count()))
    mean_plt = plt.plot(means, "".join(['-',col]), linewidth=2)
    # med_plt = plt.plot(meds,"".join(['-',col]), linewidth=1, color='r')
    med_plt = []
    if col=='bo':
        plt.plot(twentyfive, "".join(['--','--b']), linewidth=0.3)
        plt.plot(seventyfive,"".join(['--','--b']), linewidth=0.3)
        plt.plot(five, "".join(['--','--b']), linewidth=0.2)
        plt.plot(ninetyfive,"".join(['--','--b']), linewidth=0.2)
    # plt.plot([i - j for i, j in zip(means,stderr)],"".join(['-.',col]), linewidth=0.3)
    # plt.plot([i + j for i, j in zip(means,stderr)],"".join(['-.',col]), linewidth=0.3)
    plt.title(y_name, fontsize=14);
    ax.set_xticklabels(range(1987,1993))

    print stderr
    
    dat = []
    if inc_dat:
        if tot == 1:
            dat = plt.plot([0.0010211027910142954, 0.0061266167460857727, 0.01055139550714772, 0.017699115044247787, 0.024506466984343091, 0.030633083730428862] , '--k', linewidth=2)
            # lag = plt.plot([0.0061266167460857727, 0.01055139550714772, 0.017699115044247787, 0.024506466984343091, 0.030633083730428862, 0.034377127297481] , '--k', linewidth=2)
        if tot == 0:  
            dat = plt.plot([0, 0.013043478260869565, 0.086956521739130432,
                      0.14782608695652175, 0.24782608695652175,
                      0.34347826086956523], '-k', linewidth=2)
        if tot == 2:
            dat = plt.plot([0.029126213592233011, 0.18446601941747573, 0.23300970873786409, 0.3300970873786408, 0.37864077669902912, 0.46601941747572817], '--k', linewidth=2)
            # lag = plt.plot([0.18446601941747573, 0.23300970873786409, 0.3300970873786408, 0.37864077669902912, 0.46601941747572817,0.50485436893203883], '--k', linewidth=2)
            # plt.ylim([0,0.4])
        if tot == 3:
            dat = plt.plot([8.4297104260220852, 3.2243277310674179, 2.4078194442922398, 1.9876055766704781, 1.6534448852644443, 1.4324822528353145], '--k', linewidth=2)
            # lag = plt.plot([3.2243277310674179, 2.4078194442922398, 1.9876055766704781, 1.6534448852644443, 1.4324822528353145, 1.3587766883477246], '--k', linewidth=2)
    lag = []
    return means, mean_plt, med_plt, dat, lag

# ADD FIRST YEAR OF ZEROS TO LAG
spreadl['cff'] = 0
spreadl['dff'] = 0
spreadl['sdf'] = np.nan

fig1 = plt.figure(figsize=(17,  8),  dpi=80)
m0, mean0, med0, dat, lag = mkplt(spreadb[['cf0','cf1','cf2','cf3','cf4','cf5']],1,1,1,r'% authors','bo',True,1)
lgd = plt.legend([mean0[0], dat[0]], ['bench', 'data'], 4)
#plt.savefig('sim_plots_cf_cf.png',bbox_inches=0)

plt.savefig('sim_plots_mc_baseline.png',bbox_inches=0)
# dif = spread2.applymap(math.log) - spread1.applymap(math.log)
# dif.to_csv('test.csv')
# 
# fig2 = plt.figure(figsize=(17,  8),  dpi=80)
# m0, mean0, med0, dat = mkplt(dif[['df0','df1','df2','df3','df4','df5']],1,3,2,r'log diff % departments','b',False,1)
# plt.plot([0,0,0,0,0,0],'--k')
# #plt.savefig('sim_plots_cf_df_frac.png',bbox_inches=0)
# 
# # fig4 = plt.figure(figsize=(17,  8),  dpi=80)
# m0, mean0, med0, dat = mkplt(dif[['cf0','cf1','cf2','cf3','cf4','cf5']],1,3,1,r'log diff % authors','b',False,1)
# plt.plot([0,0,0,0,0,0],'--k')
# #plt.savefig('sim_plots_cf_cf_frac.png',bbox_inches=0)
# 
# # fig6 = plt.figure(figsize=(17,  8),  dpi=80)
# m0, mean0, med0, dat = mkplt(dif[['sd0','sd1','sd2','sd3','sd4','sd5']],1,3,3,r'log diff % department sd','b',False,1)
# plt.plot([0,0,0,0,0,0],'--k')
# plt.savefig('sim_plots_cf_frac.png',bbox_inches=0)

# fig7 = plt.figure(figsize=(17,  8),  dpi=80)
# m0, mean0, dat = mkplt(spread0[['ds0','ds1','ds2','ds3','ds4','ds5']],1,1,1,r'% departments','b',True,2)
# m1, mean1, dat = mkplt(spread1[['ds0','ds1','ds2','ds3','ds4','ds5']],1,1,1,r'% departments','r',True,2)
# m2, mean2, dat = mkplt(spread2[['ds0','ds1','ds2','ds3','ds4','ds5']],1,1,1,r'% departments','y',True,2)
# lgd = plt.legend([dat[0], mean0[0], mean1[0], mean2[0]], ['data', 'full', 'nolat', 'nolat_nobet'], 4)
# plt.savefig('sim_plots_comp_df_dat.png',bbox_inches=0)
# 
# fig8 = plt.figure(figsize=(17,  8),  dpi=80)
# m0, mean0, dat = mkplt(spread0[['dd0','dd1','dd2','dd3','dd4','dd5']],1,1,1,r'department std devs','b',True,3)
# m1, mean1, dat = mkplt(spread1[['dd0','dd1','dd2','dd3','dd4','dd5']],1,1,1,r'department std devs','r',True,3)
# m2, mean2, dat = mkplt(spread2[['dd0','dd1','dd2','dd3','dd4','dd5']],1,1,1,r'department std devs','y',True,3)
# lgd = plt.legend([dat[0], mean0[0], mean1[0], mean2[0]], ['data', 'full', 'nolat', 'nolat_nobet'], 4)
# plt.savefig('sim_plots_comp_sd_dat.png',bbox_inches=0)
plt.show()

# [0.0061266167460857727, 0.01055139550714772, 0.017699115044247787, 0.024506466984343091, 0.030633083730428862, 0.034377127297481283, 0.038121170864533697]
# [0.18446601941747573, 0.23300970873786409, 0.3300970873786408, 0.37864077669902912, 0.46601941747572817, 0.50485436893203883, 0.55339805825242716]
# [nan, 8.4297104260220852, 3.2243277310674179, 2.4078194442922398, 1.9876055766704781, 1.6534448852644443, 1.4324822528353145, 1.3587766883477246, 1.2490128572962629]
