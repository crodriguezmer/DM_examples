# -*- coding: utf-8 -*-
"""
This script opens subject files and searches for a random trial to determine 
payment. It is set-up to ignore empty non-collected blocks and non-response 
trials.

Created on Tue Oct 28 16:33:14 2014

@author: christianrodriguez
"""

# Set-up the directory
#resultsdir = '/Users/christianrodriguez/Dropbox/Python/data'
resultsdir = '/Users/Marjolein/Dropbox/Python/data'
# Get the subject number
subject_code = input('Enter subject number: ')

# import useful modules
import random, os, numpy, datetime
from glob import glob

# look for available files for this subject
os.chdir(resultsdir)
subj_files = glob('WMITC_%d_*' % subject_code)

# load file get a random trial
valid = False
while not valid:
    
    # randomly pick one file and load contents
    randfile = random.randint(0,len(subj_files)-1)
    data = numpy.genfromtxt('%s' % subj_files[randfile], delimiter=',', skip_header=1)
    
    # pick a random trial if there are any in file
    if len(data.shape) > 1: # skip file if empty or contains only one trial
        trial = random.randint(0,len(data)-1)
        
        # get trial details
        details=data[trial,]
        if not numpy.isnan(details[7]):
            valid = True

# print lottery outcome
print('\n\nBlock %d, trial %d' % (randfile+1, trial+1))

# Get today's date
date = datetime.date.today()
datenum = datetime.date.today().toordinal()

# Write text to screen
print('Your choices were $%.2f in %.0f days or $%.2f in %.0f days' % 
        (round(details[3],1), details[4], round(details[5],1), details[6]))
if details[7]:
    outcome = (round(details[5],1),details[6])
elif not details[7]:
    outcome = (round(details[3],1),details[4])    
print('You chose $%.2f in %.0f days' % (outcome[0],outcome[1]))
#print('Today is %s' % date.strftime("%B %d, %Y"));
paydate = date.fromordinal(int(datenum + outcome[1]))
print('That means your payment will be $%.2f on %s\n\n' % (outcome[0], paydate.strftime("%B %d, %Y")))


