#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 16 14:19:34 2014

Usage: [k, m, LL] = FitK(data)

Returns best fitting k for the discount function V=r/(1+kd).
Input data must contain individual trials in rows with columns
  [r1 d1 r2 d2 choice]
for choices betwen r1 at delay d1 and r2 at delay d2. choice must
be 0 for choice of option (r1,d1) or 1 to indicate choice of (r2,d2).
Fitting is for maximum likelihood with a softmax function. m is the
best fitting slope of the softmax function. Larger values of m
indicate a better quality fit. LL is the log-likelihood of the best fit. 
This is useful for statistical analysis of the significance of fitted 
parameters (i.e. likelihood ratio test).

@author: christianrodriguez 
Check out:
http://psych.stanford.edu/~dnl/
http://en.wikipedia.org/wiki/Hyperbolic_discounting

"""

def fitk(data):
    
    from scipy import optimize
    import numpy, math
    
    # make some shortcuts
    nprand  = numpy.random.rand

    global d
    d = data
    LL = float('inf')
    
    # optimize parameters 100 times, using different starting points
    randstarts = 0
    while randstarts < 1000:
        
        # pick random initial values
        km0 = [nprand() * .02, nprand() * 2]
    
        opts = {'maxiter':10000}
        bnds = ((0,1), (0,200)) 
        res = optimize.minimize(errorfit, km0, bounds=bnds, options=opts,\
                                method='L-BFGS-B') #method='L-BFGS-B' TNC
    
        # evaluate the softmax at the given values                 
        loglike = errorfit(res.x)

        # use the new values if the loglikelihood is decreased
        if loglike < LL and not(math.isinf(loglike)):
            km = res.x
            LL = loglike
            
        randstarts = randstarts + 1

    # output k, m, and loglikelihood
    return km[0], km[1], -1*LL, res

#    # make a summary plot
#    plotFit(km)

def errorfit(km):
    
    #d = fitkd
    '''
    Computes -1*loglikelihood of softmax fit assuming hyperbolic discounting.
    '''
    
    import numpy
    
    # make some shortcuts
    concat  = numpy.concatenate
    nplog   = numpy.log
    npexp   = numpy.exp
    npnot   = numpy.logical_not
    npsum   = numpy.sum
            
    # discounted values based on current k guess
    V1 = d[:,0]/(1 + km[0]*d[:,1]) # Vss
    V2 = d[:,2]/(1 + km[0]*d[:,3]) # Vll
    
    # p of choosing ll (ll=2)
    pll = 1/(1+ npexp(-km[1]*(V2-V1))) 
    
    # boolean of ll choices
    lls = d[:,4]==1 

    # penalize contradictions (ll and pll=0 or ss and pll=1)
    if 0 in pll[lls] or 1 in pll[npnot(lls)]:
        loglik = float('inf') # maximum float, avoids inf errors
    else:
        loglik = npsum(  nplog( concat( ( pll[lls], 1-pll[npnot(lls)] ) ) ) )
            
    return  -1*loglik

def plotfit(km):
    
    #d = fitkd
    '''
    Make various fit diagnostic plots.
    '''
    
    import numpy
    import matplotlib.pyplot as plt
        
    # make some shortcuts
    npmax   = numpy.amax
    plot    = plt.plot
    subplot = plt.subplot
    nparray = numpy.array
    nprange = numpy.arange
    axis    = plt.axis
    npmin   = numpy.amin
    npexp   = numpy.exp


    # get range of x axis
    maxd1 = npmax(d[:,1])
    maxd2 = npmax(d[:,3])
    mind1 = npmin(d[:,1])
    mind2 = npmin(d[:,3])
    mind  =  npmin(nparray([mind1, mind2]))
    maxd  =  npmax(nparray([maxd1, maxd2]));

    # make a smooth delay range from 0
    t = nprange(0, maxd, .1)

    # open a new figure
    plt.figure()    
    
    subplot(1,3,1)
    plot(t, 1/(1+km[0]*t), '-k')
    plt.xlabel('t')
    plt.title('1/(1+kt)') #y.labels get crowded
    
    # make arrays of delays and discounted values
    ss = d[:,4] == 0
    delayss =  (d[ss,1], d[ss,3])
    valss   =  ( d[ss,0]/(1+km[0]*d[ss,1]), d[ss,2]/(1+km[0]*d[ss,3]) ) 
    ll = d[:,4] == 1
    delayll =  (d[ll,1], d[ll,3])
    valll   =  ( d[ll,0]/(1+km[0]*d[ll,1]), d[ll,2]/(1+km[0]*d[ll,3]) ) 
   
    subplot(1,3,2)
    plot( delayss, valss, 'o-r')
    axis([0, npmax(delayss), 0, npmax(valss)])
    plot( delayll, valll, 'o-b')
    axis([0, npmax(delayll), 0, npmax(valll)])
    plt.xlabel('t')
    plt.title('SV') #y.labels get crowded
    
    # discounted values based on current k guess
    V1 = d[:,0]/(1 + km[0]*d[:,1]) # Vss
    V2 = d[:,2]/(1 + km[0]*d[:,3]) # Vll
    netval = V2-V1
    
    # p of choosing ll (ll=2)
    pll = 1/(1+ npexp(-km[1]*(V2-V1))) 
    
    subplot(1,3,3)
    plot( netval, pll, 'og')
    plot( netval[ss], d[ss,4], 'or')
    plot( netval[ll], d[ll,4], 'ob')
    plt.xlabel('V(ll)-V(ss)')
    plt.title('p(ll)') #y.labels get crowded
