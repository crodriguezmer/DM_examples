#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This script takes a table of subject specific offers generated using staircase
parameter fits. An explanation of how offers are generated can be found in the
offer generator script, 'Gen_WMITC_offers.py'. The experiment is divided into 
four runs where a quarter of the offers are presented. Each trial presents a 
fixation cross for .5s, then a fixed offer for 1.5s. The first offer could be 
an SS or LL. Then a fixation cross is presented for 6 seconds before the 
probability adjusted offer is presented for a maximum of 4 seconds. The ITI 
goes from 2-3 seconds, with uniform jitter.
 
Check out:
http://en.wikipedia.org/wiki/Hyperbolic_discounting

"""

# define settings
fbutton  = '2'      # button code for selecting the first option
sbutton  = '3'      # button code for selecting the second option
white = (255,255,255) # default used is gray
instsize = 30         # a reasonable size for instructions text
tsize = 60            # a large size for offer text
crossize = (int(tsize*.8), int(tsize*.8)) # smaller is prettier
amtpos = (0,.5*tsize)    # relative position for amount, center = (0,0)
delpos = (0,-.5*tsize)   # relative position for delay
fixcprest = 500       # time for fix-cross presentation (ms)
foprest = 1500        # time for first offer presentation (ms)
dprest  = 6000        # length of delay period (ms)
maxdt   = 5000        # max decision time, presentation of second offer (ms)
itir    = (2000,3001) # range for inter-stimulus-interval
secs = 10             # seconds to wait if warining screen is ran


from expyriment import design, control, stimuli, misc
import os, serial
import numpy as np

# make sure the script runs on the appropriate directory
maindir = '/Users/christianrodriguez/Dropbox/Python'
os.chdir(maindir)

# indicate the run number (x/4)
blck = input('What run will this be? (1-4)   ')

# Create and initialize an Experiment
exp = design.Experiment('WM ITC')
control.defaults.initialize_delay = 0
control.initialize(exp)

# shortcut to the keyboard
response_device = exp.keyboard

# preload fixation cross for ITI
fixcross = stimuli.FixCross(colour=white, size= crossize)
fixcross.preload()

# name variables to be collected
exp.data_variable_names = ['run','trial', 'famnt', 'fdel', 'pamnt', 'pdel',
                           'choice', 'RT','foffert','dtime','poffert']

# Start Experiment
control.start(skip_ready_screen=True)

# get subject number and load stimulus file, notify if stim file doesnt exist
subj = exp.subject
try:
    offers = np.genfromtxt('%s/data/offers/%s_offers.txt' % (maindir, subj),
                           delimiter=',', skip_header=1)
except IOError: 
    control.end(goodbye_text=None, goodbye_delay=None, fast_quit=None)
    print('The subject number you entered (%s) does not have a stimulus file.'
    % (subj))
  
# select the stimuli to be presented
if blck == 1:
    offers = offers[:40,:]
elif blck == 2: 
    offers = offers[40:80,:]
elif blck == 3: 
    offers = offers[80:120,:]
elif blck == 4: 
    offers = offers[120:,:]
else:
    control.end(goodbye_text=None, goodbye_delay=None, fast_quit=None)
    print('The run number should be between 1 and 4.')
  
# present instruction screen
instrcs = []
instrcs = instrcs + ["In this task you will again choose between two payment offers. \
However, both offers will now appear on the center of the screen and there will \
be a delay of a few seconds in between the two. A fixation cross will appear \
in the center of the screen just before the first offer and during the delay \
period. The screen will be blank for a few seconds in between trials. \
\n\n\
To help you keep track of which stage of the trial you are in, the first offer \
will appear in yellow and the second offer will appear in green. As soon as \
you see the green offer you'll have all the information you need and should \
indicate your decision. So you should press the button indicating your decision \
while the green offer is on the screen. \
\n\n\
Press any key to see more instructions."]

instrcs = instrcs + ["To indicate that you prefer the offer that appears first, \
press the left button (yellow). Conversely, to indicate that you prefer the \
offer that appears after the delay, press the right button (green). Make sure \
you press the buttons with either your index or middle finger. \
\n\n\
Just like before, PLEASE AVOID USING ANY EXPLICIT RULES. \
\n\n\
Press any key to start the task."]

# present instruction screens
if blck == 1:
    screennum = 1
    for insts in instrcs:
        stimuli.TextScreen('Instructions (%d/%d)' % (screennum, len(instrcs)), 
                           insts, text_size= instsize, text_colour= white, 
                           heading_colour= white, heading_size=instsize).present()
        response_device.wait()
        screennum = screennum + 1

## communicate with scanner
ser = serial.Serial('/dev/tty.usbmodem12341', 57600, timeout=1) # open port
ser.write("[t]") # start the scanner
ser.close() # close port

# start clock and get the a relative t = 0 mark
clock = misc.Clock()
strtt = clock.monotonic_time()
          
# wait for several seconds to allow for signal saturation
while secs > 0:
    intro = 'The task will start in %d seconds' % secs
    stimuli.TextScreen('', intro, text_size= instsize, 
                       text_colour= white).present()
    exp.clock.wait(1000)
    secs = secs - 1

# loop for specified number of trials
trial = 0
while trial < len(offers):
    
    # present fixation cross and wait sometime
    fixcross.present()
    exp.clock.wait(fixcprest)
    
    
    # get the fixed offer, present and wait for sometime
    foffer = offers[trial,:2]
    famnt = '$'+'%.2f' % (np.round(foffer[0], decimals = 1))
    if foffer[1] == 0:
        fdel = 'Today'
    else:
        fdel = '%.0f' % (foffer[1])+' days'
        
    screen = stimuli.BlankScreen()
    stim1 = stimuli.TextLine(text=famnt, position=amtpos, 
                             text_colour=(255,255,0), text_size = tsize)
    stim2 = stimuli.TextLine(text=fdel, position=delpos, 
                             text_colour=(255,255,0), text_size = tsize)
    stim1.plot(screen)
    stim2.plot(screen)
    screen.present()
    foffert = clock.monotonic_time() - strtt # when the first offer appears
    exp.clock.wait(foprest)
    
    # present fixation cross and wait sometime
    fixcross.present()
    dtime = clock.monotonic_time() - strtt # when the fix-cross appears
    exp.clock.wait(dprest)
    
    # get probability adjusted offer, present and wait (some max  time) for resp
    poffer = offers[trial,2:]
    pamnt = '$'+'%.2f' % (np.round(poffer[0], decimals = 1))
    if poffer[1] == 0:
        pdel = 'Today'
    else:
        pdel = '%.0f' % (poffer[1])+' days'
    
    screen = stimuli.BlankScreen()    
    stim3 = stimuli.TextLine(text=pamnt, position=amtpos,
                            text_colour=(0,255,0), text_size = tsize)
    stim4 = stimuli.TextLine(text=pdel, position=delpos,
                            text_colour=(0,255,0), text_size = tsize)
    stim3.plot(screen)
    stim4.plot(screen)
    screen.present()
    poffert = clock.monotonic_time() - strtt # when the second offer appears
    button, rt = response_device.wait_char([fbutton,sbutton], duration=maxdt)
    
    # present random ITI screen
    screen = stimuli.BlankScreen().present()
    exp.clock.wait(np.random.randint(itir[0],itir[1]))
            
    # code choices
    if button is None:
        choice = float('nan')
        rt = float('nan')
    elif ((foffer[0] == 40) and (fbutton in button)) or ((foffer[0] == 20) and (sbutton in button)):
        choice = 1
    elif ((foffer[0] == 20) and (fbutton in button)) or ((foffer[0] == 40) and (sbutton in button)):
        choice = 0 
        
    # add data to file
    exp.data.add([blck, trial, float(foffer[0]), float(foffer[1]),
                  float(poffer[0]), float(poffer[1]), choice, rt, 
                  foffert, dtime, poffert])
                  
    # move onto next trial              
    trial = trial + 1

# End Experiment
control.end(goodbye_text=None, goodbye_delay=None, fast_quit=None)