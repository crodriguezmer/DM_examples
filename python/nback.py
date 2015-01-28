#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This script runs an n-back task. The stimuli are written in a csv file. 
Different conditions are written in different files. Currently only 1 and 2
back conditions are implemented. Once the stimuli are built into a list the 
script treats each row of letters as a block and each letter as a trial. General
task instructions are presented first. Code to start an MRI scanner through a 
serial port can then be ran. Some code to allow for signal saturation can also 
be ran or get commented out. Before the letter stream starts, the condition 
intruction screen is presented. The letters then appear with fixation cross 
periods in between letters. After a whole block of letters the script waits some
time and moves on. The subject responses are logged along with the start times
for bloks and trials. 

For some background see: http://en.wikipedia.org/wiki/N-back

Created on Fri Oct 17 14:19:10 2014

@author: christianrodriguez
"""

# define stimuli settings
ntbutton = '2' # button code for non-targets
tbutton  = '3' # button code for targets
white = (255,255,255) # default used is gray
instsize = 30         # a reasonable size for instructions text
tsize = 80            # a large size for letter stimuli
crossize = (int(tsize*.5), int(tsize*.5)) # smaller is prettier
pos = (0,-10)        # relative position for stimuli, (hor,ver); center = (0,0)
stimt = 500          # time for stimulus presentation (ms)
iti = 2500           # time between trials (ms)
ibir = (8000,10000)  # range of time between blocks (ms)
inst = 2000          # time for block instruction presentation (ms)
secs = 10            # seconds to wait if warining screen is ran

from expyriment import design, control, stimuli, misc
import os, random, serial

# make sure the script runs on the appropriate directory
maindir = '/Users/christianrodriguez/Dropbox/Python'
stimdir = '%s/data/nbackstim' % maindir
os.chdir(maindir)

# open files and organize stimuli
stims = [] # prealocate a list 
f1 = open('%s/stim1back.csv' % stimdir, 'r') # open 1-back stim file
tmp = f1.readlines() # get contents
for line in tmp:  # loop through each row
    line = line.rstrip() # eliminate new line characters 
    line = line.replace(',','') # eliminate commas
    stims = stims + [line] # place row in list
f2 = open('%s/stim2back.csv' % stimdir, 'r') # open 2-back stim file, repeat...
tmp = f2.readlines() 
for line in tmp:  
    line = line.rstrip() 
    line = line.replace(',','') 
    stims = stims + [line]

# Create and initialize an Experiment
exp = design.Experiment('WM Nback')
control.defaults.initialize_delay = 0
control.initialize(exp)

## select keyboard or create IO
response_device = exp.keyboard

# preload fixation cross for ITI
fixcross = stimuli.FixCross(colour=white, size= crossize)
fixcross.preload()

# name variables to be collected
exp.data_variable_names = ['block','cond','trial','resp','RT','correct',
'blctime','trltime']

# Start Experiment        
control.start(skip_ready_screen=True)

# make instruction screens
instrcs = []
instrcs = instrcs + ["In this task we will present you some letter streams in the \
center of the screen. You will need to indicate if the letter you are seeing \
is the same as the letter you saw 1 or 2 trials before. You will complete \
several blocks, and we will let you know before each block if you need to \
follow the 1-back or the 2-back rule. \
\n\n\
In 1-back blocks you will look for consequtive repetitions. For example, \
if you see the sequence 'b T t', you should indicate that the first two \
letters are not targets and that the third is a target, because it is the same \
as the letter that appeared 1 trail before. As you can see, letter case does \
not matter. \
\n\n\
Press any key to see more instructions."]

instrcs = instrcs + ["During 2-back blocks you are looking for non-consequtive \
repetitions. So, if you saw the sequence 'T b t', you should indicate that the \
first two letters are not targets and that the third is a target, because it is \
the same as the letter that appeared 2 trials before. \
\n\n\
The indication of which rule you will need to follow will appear on the center \
of the screen for two seconds. Then the letter stream will start. To indicate \
that the letter on the screen is not a target, you should press the left button \
(yellow). Conversely, to indicate that the letter on the screen is a target, you \
should press the right button (green). You should respond as soon as possible \
after a letter appears, and you should respond to every letter, starting from the \
first. \
\n\n\
Press any key to see more instructions."]

instrcs = instrcs +["Make sure you press the buttons with either your index or \
middle finger. The letters will be on the screen for a brief period of time. \
You will see a fixation cross appear in the center of the screen, for a couple \
of seconds, between each letter presentation. There will be a break of several \
seconds between blocks. During this time you can relax, but you should still \
not move. \
\n\n\
Press any key to start the task."]

# present instruction screens
screennum = 1
for insts in instrcs:
    stimuli.TextScreen('Instructions (%d/%d)' % (screennum, len(instrcs)), 
                       insts, text_size= instsize, text_colour= white, 
                       heading_colour= white, heading_size=instsize).present()
    response_device.wait()
    screennum = screennum + 1

# communicate with scanner
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

# counterbalance the block order
order = random.sample(range(len(stims)),len(stims))

# loop through blocks in order
blckscompleted = 0

for blocknum in order:
    
    blctime = clock.monotonic_time() - strtt # when the block starts
    
    # start trial count
    trialnum = 0
    
    # present the block type for 2 seconds
    if blocknum < 4:
        text = 'Get ready for 1-back.'
        cond = 1
    else:
        text = 'Get ready for 2-back.'
        cond = 2
        
    stimuli.TextScreen('', text, text_size= tsize, text_colour=white).present()
    exp.clock.wait(inst)

    # present trials
    for trial in stims[blocknum]:
        
        trltime = clock.monotonic_time() - strtt # when the trial starts
    
        # get the fixed offer, present and wait for some time       
        screen = stimuli.BlankScreen()
        stim1 = stimuli.TextLine(text=trial, position=pos,
                                 text_size=tsize, text_colour=white)
        stim1.plot(screen)   
        screen.present()
        
        # collect response if it happens during presentation
        button, rt = response_device.wait_char([ntbutton,tbutton], 
                                               duration=stimt)
        if rt is not None:
            exp.clock.wait(stimt-rt)
        
        # present fixation cross for some time
        fixcross.present()
        # if a response hasn't been made give another chance
        if rt is None:
            button, rt = response_device.wait_char([ntbutton,tbutton],
                                                   duration=iti)
            if rt is not None:            
                exp.clock.wait(iti-rt)
        else: # otherwise just present the delay window
            exp.clock.wait(iti)
            
        # mark if response was correct
        stimletter = trial.lower()
        correct    = 0  # default to error and revise below
            
        if cond == 1 & trialnum >= 1: # the 1-back case
            maybtarget = True
            nbletter = stims[blocknum][trialnum-1].lower() # get the target
                
        elif cond == 2 & trialnum >= 2: # the 2-back case
            maybtarget = True
            nbletter = stims[blocknum][trialnum-2].lower() # get the target
                
        else: # when there are no possible targets
            maybtarget = False
                
            if button == ntbutton:                 
                correct = 1
            
        if maybtarget:
            if (stimletter == nbletter) and button == tbutton: # apply rule
                correct = 1
            elif (stimletter != nbletter) and button == ntbutton:
                correct = 1

        # add data to file
        exp.data.add([blocknum, cond, trialnum, button, rt, correct,
                      blctime, trltime])
        
        # move to the next trial
        trialnum = trialnum + 1
        
    # move to next block
    blckscompleted = blckscompleted + 1
        
    # wait between blocks
    if blckscompleted < len(stims):
        stimuli.TextScreen('', 'This is a rest period. Relax!',
                       text_size= instsize, text_colour=white).present()
        ibi = random.randint(ibir[0],ibir[1])
        exp.clock.wait(ibi)

# End Experiment
control.end(goodbye_text=None, goodbye_delay=None, fast_quit=None)