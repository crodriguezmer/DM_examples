#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This script generates 160 offers for an intertemporal choice experiment. The 
trials are generated such that one of the offers is always specified a priori
and the other is adjusted to satisfy a choice probability constraint. The 
specifications can be changed to satisfy whatever delay, amount, and choice 
probability parameters are desired. Below are the params currently implemented.

Fixed offers:
SS: $20 in 0 or 15 days
LL: $40 in 30 or 60 days

Probability adjusted offers:
Delays: 0-15 days for SS; 30 to 60 days for LL
P(LL): .1, .4, .6, .9

Created on Wed Sep 17 20:21:11 2014
@author: christianrodriguez
"""

# set parameters
ssa  = 20 
ssd1 = 0
ssd2 = 15
lla  = 40
lld1 = 15
lld2 = 60
pll  = [.1, .4, .6, .9]
tsperbin = 40

# specify directories
datdir    = '/Users/christianrodriguez/Dropbox/Python/data'
paramsdir = '/Users/christianrodriguez/Dropbox/Python/data/fitted'
offersdir = '/Users/christianrodriguez/Dropbox/Python/data/offers'

import os 
import numpy as np

# make sure offersdir exists
if  not os.path.isdir(offersdir):
    os.mkdir(offersdir)

# ask for subject number and get choice parameters
subn = input('Which subject do you want to run?  ')
# fill in with a leading zero for file name
subn = subn.__str__().zfill(2)
fitfilen = '%s/%s_fitkparams.txt' % (paramsdir, subn)
kmll = np.genfromtxt(fitfilen, delimiter=',', skip_header=1)
k = kmll[0]
m = kmll[1]
ll = kmll[2]

# make fixed offers
sss   = np.array(np.ones((tsperbin*2,1)))*ssa
sssd1 = np.array(np.ones((tsperbin,1)))*ssd1
sssd2 = np.array(np.ones((tsperbin,1)))*ssd2
fss   = np.concatenate((sss,np.concatenate((sssd1,sssd2),0)),1)

lls   = np.array(np.ones((tsperbin*2,1)))*lla
llsd1 = np.array(np.ones((tsperbin,1)))*lld1
llsd2 = np.array(np.ones((tsperbin,1)))*lld2
fll   = np.concatenate((lls,np.concatenate((llsd1,llsd2),0)),1)

# make probability adjusted offers
ps  = np.tile(pll, len(fss)/len(pll))
# first for fixed ss trials
pss = np.zeros((len(fss), 2))
row = 0
while row < len(pss): 
    svss  = fss[row,0]/(1+k*fss[row,1])           # hyperbolic discounted value
    psvll = svss - np.log(1/ps[row]-1)/m                # softmax value for ll 
    pss[row, 1] = np.random.randint(lld1 +1, high=lld2)    # delay of ll offer
    # add a day to the minimum p adjusted ll, to prevent trivial offers    
    pss[row, 0] = round(psvll + psvll*k*pss[row, 1], 2) # amount of ll offer
    row = row + 1
fsstrials = np.concatenate((fss,pss),1)
# then for fixed ll trials
pll = np.zeros((len(fll), 2))
row = 0
while row < len(pll): 
    svll  = fll[row,0]/(1+k*fll[row,1])           # hyperbolic discounted value
    psvss = svll + np.log(1/ps[row]-1)/m                # softmax value for ss 
    pll[row, 1] = np.random.randint(ssd1, high=ssd2)    # delay of ss offer
    pll[row, 0] = round(psvss + psvss*k*pll[row, 1], 2) # amount of ss offer
    row = row + 1
flltrials = np.concatenate((fll,pll),1)

# collect all trials, shuffle and store in file for experiment
offers = np.random.permutation(np.concatenate((fsstrials, flltrials)))
np.savetxt('%s/%s_offers.txt' % (offersdir, subn), offers, delimiter=',',
           fmt='%.2f',header='"famnt","fdelay","pamnt","pdelay"')
