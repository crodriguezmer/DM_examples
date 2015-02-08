#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This script runs a staircase procedure that estimates a subject's temporal 
discounting preferences, asuming a hyperbolic discounting function. The smaller
sooner offer is selected from a small range of options. Delays for the larger
offer are selected with uniform probability, from a range of between 16 and 45 
days.
 
Check out:	
http://en.wikipedia.org/wiki/Hyperbolic_discounting

"""

from expyriment import design, control, stimuli
import random, numpy, os

# make sure the script runs on the appropriate directory
#os.chdir('/Users/christianrodriguez/Dropbox/Python')
os.chdir('/Users/Marjolein/Dropbox/Python')

# Create and initialize an Experiment
ntrials = 60
kval = .02
step = .01
box_size = (100, 100)
exp = design.Experiment('WM ITC')
control.defaults.initialize_delay = 0
control.initialize(exp)

# Define screen settings
ssize = exp.screen.window_size
hdist = .2*ssize[0]
vdist = 0
sspos = (-hdist,vdist)
llpos = (hdist,vdist)

# select keyboard or create IO (IO requires import io)
#response_device = io.EventButtonBox(io.SerialPort("/dev/ttyS1"))
response_device = exp.keyboard

# prepare and preload instruction screen
instructs = "In this task you will see two delayed payment offers appear on \
the left and right side of the screen. For example, you may see an offer like \
$10 in 15 days on the left and $20 in 30 days on the right. Your job is to \
evaluate these options and choose the payment that you'd  prefer to receive. \
If you prefer the option on the left you will indicate that by pressing the \
'f' key. To select the option on the right you'd press the 'j' key. \n\n\n\
\
PLEASE AVOID USING CUTOFF RULES. For example, you may be tempted to always \
select the larger amount, without considering the delay, or to take the larger \
amount if it offers more than a certain amount of dollars per day. If you adopt a \
cutoff rule like these examples we would be looking more at your math skills \
than your subjective preferences. We would like you to choose base on your \
'gut feeling' about the attractiveness of the offers.\n\n\n\
\
Because this is a practice task, we will not time you, so feel free to take as \
long as you need on each trial. A fixation cross will appear between trials. \
You can take that time to blink or just wait for the next trial.\n\n\n\
\
Press any key to start the task."

# staircase scren builder
def itc_stair(kval, curr_trial):
    
    screen = stimuli.BlankScreen()
    
    # make the offer strings to place on screen
    ss = random.choice([(10, 0), (10, 15), (20,0), (20, 15)])
    ssval = ss[0]/(1+kval*ss[1])
    
    if ss[1]==0:
        sstext = '$'+'%.2f' % (ss[0])+'\nToday'
    else:
        sstext = '$'+'%.2f' % (ss[0])+'\n'+str(ss[1])+' days'
        
    lldel = random.randint(16,45)
    llamt = round(ssval+ssval*kval*lldel,1)
    lltext = '$'+'%.2f' % llamt+'\n'+str(lldel)+' days'
    
    lstim = stimuli.TextBox(text=sstext, size=box_size, position=sspos, \
            text_justification=1)
    lstim.plot(screen)
    rstim = stimuli.TextBox(text=lltext, size=box_size, position=llpos, \
            text_justification=1)
    rstim.plot(screen)
    screen.present()
    return ss, llamt, lldel
      
# preload fixation cross for ITI
fixcross = stimuli.FixCross()
fixcross.preload()

# Start Experiment
exp.data_variable_names = ['trial', 'k', 'ssamnt', 'ssdel', \
                            'llamnt', 'lldel', 'choice', 'RT']
control.start(skip_ready_screen=True)

# present instructions
stimuli.TextScreen("Instructions", instructs).present()
response_device.wait()
  
# loop for specified number of trials
trial = 0
kvals = numpy.array([kval])
while trial < ntrials:
    
    # present trial
    ss, llamt, lldel = itc_stair(kval, trial)
    
    # collect behavior
    button, rt = response_device.wait_char(['f','j'])
    
    # present ITI screen
    fixcross.present()
    exp.clock.wait(random.randint(300,500))

    # adjust the k estimate
    if 'f' in button:
        kval = kval + step
        ll = 0
    elif 'j' in button:
        kval = kval - step
        ll = 1
        
    # keep track of k values
    kvals = numpy.concatenate((kvals, numpy.array([kval])))
        
    # decrease step size if a k is revisited within 5 consequetive trials
    if trial > 4 and len(numpy.unique(kvals[-5:]))<=4:
        step = step *.95
    
    # add data to file
    exp.data.add([trial, round(kval,3), ss[0], ss[1], llamt, lldel, ll, rt])
    trial = trial + 1

# End Experiment
control.end(goodbye_text=None, goodbye_delay=None, fast_quit=None)
#execfile('runFitK.py',)