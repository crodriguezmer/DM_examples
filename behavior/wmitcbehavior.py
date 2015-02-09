
# coding: utf-8

## script set up

# import all the necesary modules
import pandas as pd 
import numpy as np 
import seaborn as sns 
import matplotlib as mpl 
import matplotlib.pyplot as plt
import statsmodels.api as sm, statsmodels.formula.api as smf
from os import chdir, getcwd
from glob import glob 
from scipy import stats as st
get_ipython().magic(u'matplotlib inline')


## get data

# switch to dir where the data lives
chdir('/Users/christianrodriguez/Dropbox/Python/data')

# look for the wanted files
filz = glob('./WMITC*')

# append all the files
data = pd.read_csv(filz[0], skiprows=9)

for f in filz[1:]:
    data = data.append(pd.read_csv(f, skiprows=9))
# data


## get choice parameters

# get a table of choice parameters
chdir('/Users/christianrodriguez/Dropbox/Python/data/fitted')
parfilz = glob('./*_fitkparams.txt')

params = pd.read_csv(parfilz[0], skiprows=0)
subids = parfilz[0][2:6].split()

for pf in parfilz[1:]:
    params = params.append(pd.read_csv(pf, skiprows=0))
    subids.append(pf[2:6])
params['subid'] = pd.Series(subids, index=params.index)
# params


## compute choice variables with hyperbolic discounting (staircase)

## make a table of choice variables (fsv, psv and pll)
# initialize vars
data['fsv'] = 0
data['ssv'] = 0

# loop through subjects
for s in subids:
    
    k = float( params['k'][params['subid'] == s ])
    m = float( params['m'][params['subid'] == s ])
    s = float(s)

    # compute variables of (fsv, ssv and pll with staircase parameters)
    data['fsv'][data['subject_id']==s] = data.iloc[:,3][data['subject_id']==s] / (1+k*data.iloc[:,4][data['subject_id']==s])
    data['ssv'][data['subject_id']==s] = data.iloc[:,5][data['subject_id']==s] / (1+k*data.iloc[:,6][data['subject_id']==s]) 

# code p for the ll offer, when the first offer is ll pll=1-ppoffer
data['psoffer'] = 1 / (1 + np.exp(-m * (data['ssv'] - data['fsv']) ) ) # round 'removes' rounding errors on offers 
data['pll'] = data['psoffer']
data['pll'][(data['famnt']==40)] = 1-data['pll'][(data['famnt']==40)] # remove weird rounding errors

# force trials into the four intended categories (needed for summary statistics)
data['pll'][data['pll']<=.25] = np.round( np.mean(data['pll'][data['pll']<=.25]) ,1)
data['pll'][(data['pll']>.25) & (data['pll']<=.5)] = np.round( np.mean(data['pll'][(data['pll']>.25) & (data['pll']<=.5)]) ,1)
data['pll'][(data['pll']>.5) & (data['pll']<=.75)] = np.round(np.mean( data['pll'][(data['pll']>.5) & (data['pll']<=.75)]), 1)
data['pll'][data['pll']>.75] = np.round( np.mean(data['pll'][data['pll']>.75]) ,1)

# data


## compute choice variables with hyperbolic discounting (scanner)

# get choice parameters
chdir('/Users/christianrodriguez/Dropbox/Python/data/fitted')
inscanparams = pd.read_csv('InScanParams.csv', skiprows=0, usecols= [1,2,3])
inscanparams['subid'] = subids
# inscanparams

# append to data
data['isfsv'] = 0
data['isssv'] = 0

# add choice variables to data
for s in subids:
    
    # select subject parameters
    isk = float(inscanparams['0'][inscanparams['subid'] == str(s) ])
    ism = float(inscanparams['0'][inscanparams['subid'] == str(s) ])
    s = float(s)
    
    # compute variables of (fsv, ssv and pll with staircase parameters)
    data['isfsv'][data['subject_id']==s] = data.iloc[:,3][data['subject_id']==s] / (1+isk*data.iloc[:,4][data['subject_id']==s])
    data['isssv'][data['subject_id']==s] = data.iloc[:,5][data['subject_id']==s] / (1+isk*data.iloc[:,6][data['subject_id']==s])
    
# code p for the second offer
data['ispsoffer'] = 1/(1+np.exp(-m * ( data['isssv'] - data['isfsv'] ) ))

# code p for the ll offer
data['ispll'] = data['ispsoffer']
data['ispll'][(data['famnt']==40)] = 1-data['ispll'][(data['famnt']==40)] 

# force trials into the four intended categories (needed for summary statistics)
data['ispll'][data['ispll']<=.25] = np.round(np.mean(data['ispll'][data['ispll']<=.25]), 1)
data['ispll'][(data['ispll']>.25) & (data['ispll']<=.5)] = np.round(np.mean(data['ispll'][(data['ispll']>.25) & (data['ispll']<=.5)]), 1)
data['ispll'][(data['ispll']>.5) & (data['ispll']<=.75)] = np.round(np.mean(data['ispll'][(data['ispll']>.5) & (data['ispll']<=.75)]), 1)
data['ispll'][data['ispll']>.75] = np.round(np.mean(data['ispll'][data['ispll']>.75]), 1)

# data


## effects of first offer type on choice

# get choice p means split by famnt type pll and subid
p = data.groupby(['subject_id','pll','famnt']).mean()['choice'].reset_index()
p = p[(p['subject_id']!=6014) & (p['subject_id']!=6016)]

pb = data.groupby(['subject_id','pll']).mean()['choice'].reset_index() 
pb = pb[(pb['subject_id']!=6014) & (pb['subject_id']!=6016)]


# model
md = smf.mixedlm('choice ~ pll * famnt', p, groups=p['subject_id'])
mdf = md.fit()
print(mdf.summary())

# model
mdb = smf.mixedlm('choice ~ pll', pb, groups=pb['subject_id'])
mdfb = mdb.fit()
print(mdfb.summary())

# plot
sns.lmplot('pll', 'choice', p, x_estimator=np.mean, hue = 'famnt')
sns.lmplot('pll', 'choice', pb, x_estimator=np.mean)
# sns.lmplot('pll', 'choice', p, x_estimator=np.mean, row = 'subject_id')


p2 = data.groupby(['subject_id','ispll','famnt']).mean()['choice'].reset_index()
p2 = p2[(p2['subject_id']!=6014) & (p2['subject_id']!=6016)]
p2b = data.groupby(['subject_id','ispll']).mean()['choice'].reset_index() 
p2b = p2b[(p2b['subject_id']!=6014) & (p2b['subject_id']!=6016)]

# model (inscan)
md2 = smf.mixedlm('choice ~ ispll * famnt', p2, groups=p2['subject_id'])
mdf2 = md2.fit()
print(mdf2.summary())

# model (inscan)
md2b = smf.mixedlm('choice ~ ispll', p2b, groups=p2b['subject_id'])
mdf2b = md2b.fit()
print(mdf2b.summary())

sns.lmplot('ispll', 'choice', p2, x_estimator=np.mean, hue='famnt')
sns.lmplot('ispll', 'choice', p2b, x_estimator=np.mean)

# sns.lmplot('ispll', 'choice', p2, x_estimator=np.mean, row='subject_id')


## compare staircase and inscan parameters

# place params of interest in dataframe 
pars = pd.DataFrame(params['k'].reset_index()['k'])
pars['isk'] = inscanparams['0'].reset_index()['0']
pars['m'] = params['m'].reset_index()['m']
pars['ism'] = inscanparams['1'].reset_index()['1']
pars = pars.drop(pars.index[[13,15]])

# run comparisons
print('k: rho, p =') 
print(st.pearsonr(pars['k'],pars['isk']))
print('k: t, p =') 
print(st.ttest_rel(pars['k'],pars['isk']))

print('m: rho, p =') 
print(st.pearsonr(pars['m'],pars['ism']))
print('m: t, p =') 
print(st.ttest_rel(pars['m'],pars['ism']))


## difficulty effects on rt

# get median RT split by famnt type pll and subid
rt = data.groupby(['subject_id','pll']).median()['RT'].reset_index() 
rt = rt[(rt['subject_id']!=6014) & (rt['subject_id']!=6016)]

# make the quadratic of pll regressor
rt['pllsqrd'] = (rt['pll']-.5)*(rt['pll']-.5)

# model 1
rtmdsqrd = smf.mixedlm('RT ~ pllsqrd', rt, groups=rt['subject_id'])
rtmdfsqrd = rtmdsqrd.fit()
print(rtmdfsqrd.summary())


# plots
sns.lmplot('pllsqrd', 'RT', rt, x_estimator=np.mean)


# repeat test with inscan params
# sumaries
rt2 = data.groupby(['subject_id','ispll']).median()['RT'].reset_index()
rt2 = rt2[(rt2['subject_id']!=6014) & (rt2['subject_id']!=6016)]


rt2['pllsqrd'] = (rt2['ispll']-.5)*(rt2['ispll']-.5)

# model 2
rtmdsqrd2 = smf.mixedlm('RT ~ pllsqrd', rt2, groups=rt2['subject_id'])
rtmdfsqrd2 = rtmdsqrd2.fit()
print(rtmdfsqrd2.summary())

# plot
sns.lmplot('pllsqrd', 'RT', rt2, x_estimator=np.mean)


# add categorical labels
data['pllsqrd'] = (data['pll']-.5)*(data['pll']-.5)
data['ispllsqrd'] = (data['ispll']-.5)*(data['ispll']-.5)


# summarize based on categories
rt3 = data.groupby(['subject_id','pllsqrd']).median()['RT'].reset_index() # get median RT split by diff and subid
rt4 = data.groupby(['subject_id','ispllsqrd']).median()['RT'].reset_index() # ditto on diff2
rt3 = rt3[(rt3['subject_id']!=6014) & (rt3['subject_id']!=6016) & (rt3['subject_id']!=6006)]
rt4 = rt4[(rt4['subject_id']!=6014) & (rt4['subject_id']!=6016) & (rt4['subject_id']!=6006)]


# ttests
print('RT on staircase diff: t, p = ')
print( st.ttest_rel(rt3['RT'][rt3['pllsqrd']<.02], rt3['RT'][rt3['pllsqrd']>.1]) )

print('RT on inscan diff: t, p = ')
print( st.ttest_rel(rt4['RT'][rt4['ispllsqrd']<.02], rt4['RT'][rt4['ispllsqrd']>.1]) )

# plot
sns.factorplot('pllsqrd','RT', data=rt3)
sns.factorplot('ispllsqrd','RT', data=rt4)




