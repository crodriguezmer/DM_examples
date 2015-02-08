#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Estimate hyperbolic parameters from the behavior observed during the fmri runs.

Created on Tue Sep 16 13:21:49 2014

@author: christianrodriguez
"""

# imports
from os import chdir
from glob import glob
import numpy as np
import pandas as pd

scriptdir = '/Users/christianrodriguez/Dropbox/Python/scripts'
datadir = '/Users/christianrodriguez/Dropbox/Python/data'

# get behavioral files
chdir(datadir)
filz = glob('WMITC_*xpd')

# make a list of subjects
subs = []
for f in filz:
    subs = subs + [f[6:10]]
subs = np.unique(subs)

# pre-allocate a params table
paramsdata = np.empty([len(subs), 3])
sindx = 0

# loop through subjects
for s in subs:
    
    # get the file names for the current subject
    subfilz = [f for f in filz if f[6:10] == s]
    
    # concatenate the data from all files for this subject
    alldata = np.genfromtxt('%s/%s' % (datadir, subfilz[0]), delimiter=',', skip_header=10)
    for f in subfilz[1:]:
        sessdata = np.genfromtxt('%s/%s' % (datadir, f), delimiter=',', skip_header=10)
        alldata = np.concatenate((alldata, sessdata))
        
    # format the data for FitK function
    data = pd.DataFrame(alldata[:,3:7])
    
    # if the first offer is $40 choice = 1 indicates choosing the first offer
    # if the first offer is $20 choice = 1 indicates choosing the second offer
    data[data.loc[:,0]==40] = data[data.loc[:,0]==40].loc[:,[2,3,0,1]]
    # now choice = 1 indicates a choice for the second column
    # append choices for second offer
    data['choice'] = alldata[:,7]
    
    # import FitK functions
    execfile('/Users/christianrodriguez/Dropbox/Python/scripts/FitK.py')
    
    # run the fitK function
    k, m, ll, res = fitk(np.array(data))
    
    # print the output to screen
    print 'k = %.5f, m = %.3f, likelihood = %.5f' % (k, m, ll)
    
    # make a summary plot
    #plotfit(np.array([k,m]))
    
    # collect values on params table
    paramsdata[sindx,:] = [k, m, ll]
    
    # move index forward
    sindx = sindx +1
    
# write a file to the fitted directory
paramsdata = pd.DataFrame(paramsdata)
paramsdata.to_csv('./fitted/InScanParams.csv')
