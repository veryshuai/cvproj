import pandas as pd
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
import math

#READ IN DATA
spread0          = pd.read_csv('spread02.csv')
spread1          = pd.read_csv('spread10.csv')
spread2          = pd.read_csv('spread_dat.csv')

def mkplt(x,sp1,sp2,sp3,y_name,col='-b',inc_dat=False,tot=False):
    ax = plt.subplot(sp1,sp2,sp3)
    xgrid = [0,1,2,3,4,5,6,7]
    means = []
    twentyfive = []
    seventyfive = []
    stderr = []
    for name in x.columns:
        des = x[name].describe()
        means.append(des['mean'])
        twentyfive.append(x[name].quantile(q=0.25))
        seventyfive.append(x[name].quantile(q=0.75))
        stderr.append(1.96 * des['std'] / math.sqrt(x[name].count()))
    mean_plt = plt.plot(means, "".join(['-',col]), linewidth=2)
    plt.plot(twentyfive, "".join(['--',col]), linewidth=0.5)
    plt.plot(seventyfive,"".join(['--',col]), linewidth=0.5)
    #plt.plot([i - j for i, j in zip(means,stderr)],"".join(['-.',col]), linewidth=0.5)
    #plt.plot([i + j for i, j in zip(means,stderr)],"".join(['-.',col]), linewidth=0.5)
    plt.title(y_name, fontsize=14)
    print stderr
    
    dat = []
    if inc_dat:
        if tot == 1:
            dat = plt.plot([0.0068337129840546698,
                            0.0091116173120728925,
                            0.015945330296127564,
                            0.020501138952164009,
                            0.025056947608200455,
                            0.027334851936218679] , '-k', linewidth=2)
        if tot == 0:  
            dat = plt.plot([0, 0.013043478260869565, 0.086956521739130432,
                      0.14782608695652175, 0.24782608695652175,
                      0.34347826086956523], '-k', linewidth=2)
        if tot == 2:
            dat = plt.plot([0.028846153846153848,
                            0.20192307692307693,
                            0.26923076923076922,
                            0.35576923076923078,
                            0.42307692307692307,
                            0.49038461538461536], '-k', linewidth=2)
        if tot == 3:
            dat = plt.plot([0.014208425594185285,
                            0.022564292366305118,
                            0.028046086930657976,
                            0.031212071828248138,
                            0.028881737442541133,
                            0.032424673992380713], '-k', linewidth=2)
    return means, mean_plt, dat

fig3 = plt.figure(figsize=(17,  8),  dpi=80)
m0, mean0, dat = mkplt(spread0[['cf0','cf1','cf2','cf3','cf4','cf5']],1,1,1,r'% authors','b',False,1)
m1, mean1, dat = mkplt(spread1[['cf0','cf1','cf2','cf3','cf4','cf5']],1,1,1,r'% authors','r',False,1)
m2, mean2, dat = mkplt(spread2[['cf0','cf1','cf2','cf3','cf4','cf5']],1,1,1,r'% authors','y',False,1)
lgd = plt.legend([mean0[0], mean1[0], mean2[0]], ['10\%', '2\%', 'model'], 4)
plt.savefig('sim_plots.png',bbox_inches=0)

fig4 = plt.figure(figsize=(17,  8),  dpi=80)
m0, mean0, dat = mkplt(spread0[['df0','df1','df2','df3','df4','df5']],1,1,1,r'% departments','b',False,2)
m1, mean1, dat = mkplt(spread1[['df0','df1','df2','df3','df4','df5']],1,1,1,r'% departments','r',False,2)
m2, mean2, dat = mkplt(spread2[['df0','df1','df2','df3','df4','df5']],1,1,1,r'% departments','y',False,2)
lgd = plt.legend([mean0[0], mean1[0], mean2[0]], ['10\%', '2\%', 'model'], 4)
plt.savefig('sim_plots_df.png',bbox_inches=0)

fig5 = plt.figure(figsize=(17,  8),  dpi=80)
m0, mean0, dat = mkplt(spread0[['sd0','sd1','sd2','sd3','sd4','sd5']],1,1,1,r'department std devs','b',False,3)
m1, mean1, dat = mkplt(spread1[['sd0','sd1','sd2','sd3','sd4','sd5']],1,1,1,r'department std devs','r',False,3)
m2, mean2, dat = mkplt(spread2[['sd0','sd1','sd2','sd3','sd4','sd5']],1,1,1,r'department std devs','y',False,3)
lgd = plt.legend([mean0[0], mean1[0], mean2[0]], ['10\%', '2\%', 'model'], 4)
plt.savefig('sim_plots_sd.png',bbox_inches=0)
# 
# fig6 = plt.figure(figsize=(17,  8),  dpi=80)
# m0, mean0, dat = mkplt(spread0[['ps0','ps1','ps2','ps3','ps4','ps5']],1,1,1,r'% authors','b',True,1)
# m1, mean1, dat = mkplt(spread1[['ps0','ps1','ps2','ps3','ps4','ps5']],1,1,1,r'% authors','r',True,1)
# m2, mean2, dat = mkplt(spread2[['ps0','ps1','ps2','ps3','ps4','ps5']],1,1,1,r'% authors','y',True,1)
# lgd = plt.legend([dat[0], mean0[0], mean1[0], mean2[0]], ['data', 'full', 'nolat', 'nolat_nobet'], 4)
# plt.savefig('sim_plots_comp_af_dat.png',bbox_inches=0)
# 
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

