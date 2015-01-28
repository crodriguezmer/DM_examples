#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 16 13:21:49 2014

@author: christianrodriguez
"""

# imports
from os import chdir
from glob import glob
import numpy

scriptdir = '/Users/christianrodriguez/Dropbox/Python/scripts'
datadir = '/Users/christianrodriguez/Dropbox/Python/data'
#scriptdir = '/Users/Marjolein/Dropbox/Python/scripts'
#datadir = '/Users/Marjolein/Dropbox/Python/data'

# get the subject number
subn = input('Which subject do you want to fit?  ')

# fill in with a leading zero for file name
subns = subn.__str__().zfill(2)

# get the file
#fname = '%s/stairK%s'
chdir(datadir)
filz = glob('stairK_%s_*xpd' % (subns))

# import the data, skipping the first 10 lines used as header
data = numpy.genfromtxt('%s/%s' % (datadir, filz[0]), delimiter=',', skip_header=10)

fitkd = data[:,3:]
fitkd = fitkd[:,:-1]

#if subn <= 8:
#    fitkd[:,-1] = 1-fitkd[:,-1] # one time exception because of error

# import FitK functions
execfile('/Users/christianrodriguez/Dropbox/Python/scripts/FitK.py')
#execfile('/Users/Marjolein/Dropbox/Python/scripts/FitK.py')

# run the fitK function
k, m, ll, res = fitk(fitkd)

# print the output to screen
print 'k = %.5f, m = %.3f, likelihood = %.5f' % (k, m, ll)

# make a summary plot
plotfit(numpy.array([k,m]))

# cd to fitKdata
if  not os.path.isdir('%s/fitted' % (datadir)):
    os.mkdir('%s/fitted' % (datadir))

# write a file to the fitted directory
f = open('%s/fitted/%s_fitkparams.txt' % (datadir, subns), 'w')
f.write('"k","m","ll"\n')
f.write('%f, %f, %f\n' % (k, m, ll))
f.close()

# get back to scriptdir and run the offer generation script
chdir(scriptdir)

#execfile('Gen_WMITC_offers.py')

