#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This script generates 8 blocks of n-back stimuli. 4 blocks are designed to be 
a 1-back task. The other blocks are designed to be a 2-back task. Each block 
consists of 25 stimuli with 8 targets. 1 and 2-back stimuli are saved to 
separate files.

Created on Wed Sep 17 20:21:11 2014
@author: christianrodriguez
"""
# specify directories
resultsdir = '/Users/.../data/nbackstim'

import random

# set parameters
numstim    = 25 
numtargets = 8
numn1bs    = 4
numn2bs    = 4
numfoils   = 2
consonants = 'bcdfghklmnpqrstvwxyz'

# make 4 blocks of 1-back
stim1back = []
blck = 1
while blck <= numn1bs:
    # pick 25 random letters with little repetition
    letters  = random.sample(consonants,len(consonants)) # as many as possible
    letters = letters + random.sample(consonants,numstim-len(consonants)) # a few more
    # make targets, avoid the last item
    trgts = random.sample(range(len(letters)-1), numtargets)
    trgts.sort() # prevent order errors
    for i in trgts:
        letters[i+1] = letters[i]
    stim1back.append(letters)
    blck = blck +1
    
# make 4 blocks of 2-back
stim2back = []
blck = 1
while blck <= numn1bs:
    # pick 25 random letters with little repetition
    letters  = random.sample(consonants,len(consonants)) # as many as possible
    letters = letters + random.sample(consonants,numstim-len(consonants)) # a few more
        # make targets, avoid the last two items
    trgts = random.sample(range(len(letters)-2), numtargets)
    trgts.sort() # prevent order errors
    for i in trgts:
        letters[i+2] = letters[i]
    stim2back.append(letters)
    blck = blck +1

# write stimuli to file
f = open('%s/stim1back.csv' % resultsdir, 'w')
for s in stim1back:
    for l in s:
        coin = random.random()
        if coin >= .5:
            l = l.upper()
        f.write('%s,' % l)
    f.write('\n')
f.close()
f = open('%s/stim2back.csv' % resultsdir, 'w')
for s in stim2back:
    for l in s:
        coin = random.random()
        if coin >= .5:
            l = l.upper()
        f.write('%s,' % l)
    f.write('\n')
f.close()


