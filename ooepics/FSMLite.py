#####################################################################
#  Copyright (c) 2023 by Paul Scherrer Institute, Switzerland
#  All rights reserved.
#  Authors: Zheqiao Geng
#####################################################################
# -------------------------------------------------
# Python based implementation of a finite state machine
# Note:
#   1. In the callback function of LocalPV/RemotePV, better not access
#      other local or remote PVs. Otherwise, a loop may be created in 
#      pyEpics and make the PV access very slow
# -------------------------------------------------
import threading
import time
import os
import queue
import sys
import traceback

from RepeatedTimer import *
from LocalPV import *

# =================================
# basic class for FSM 
# =================================
class FSMLite:
    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    # create the object
    #
    # inputs:
    #   mod_name    - string, module name
    #   fsm_name    - string, name of FSM
    #   timer_intv  - float, interval of timer, s
    #   max_try     - int, max number of try if there is failure
    #   states      - list of string, the states 
    #   state_tr    - dict, state transit table
    #   mon_func    - function, monitoring function executed when FSM is not running
    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, mod_name = '', fsm_name = '', timer_intv = 1, max_try = 3, states = [], state_tr = {}, mon_func = None):
        # save the input info and check
        self.mod_name   = mod_name
        self.fsm_name   = fsm_name
        self.timer_intv = timer_intv if (0.01 < timer_intv < 10) else 1
        self.max_try    = max_try if (max_try > 0) else 3
        self.states     = states
        self.state_tr   = state_tr
        self.mon_func   = mon_func

        if (not isinstance(states, list)) or \
           (not isinstance(state_tr, dict)) or \
           len(states) < 1 or \
           len(state_tr.keys()) < 1 or \
           not all([s in states for s in state_tr.keys()]):
            self.postMsg('ERROR: wrong states or state transit table!')
            return

        # FSM variables
        self.next_state     = self.states[0]
        self.current_state  = self.states[0]
        self.last_state     = None

        self.entry_time     = time.time()                                       # time when enter an state
        self.stay_time      = 0.0                                               # time passed staying in a state
        self.try_cnt_entry  = 0                                                 # count how many times tried
        self.try_cnt_trans  = 0
        self.try_cnt_exit   = 0

        # local PVs for the FSM
        self.lpv_cmdStart = LocalPV(self.mod_name, self.fsm_name, "START",  "", "", 1, "bo", "start/resume FSM")
        self.lpv_cmdStop  = LocalPV(self.mod_name, self.fsm_name, "STOP",   "", "", 1, "bo", "stop FSM")
        self.lpv_cmdReset = LocalPV(self.mod_name, self.fsm_name, "RESET",  "", "", 1, "bo", "reset FSM")

        self.lpv_setMaxTry = LocalPV(self.mod_name, self.fsm_name, "MAX-TRY", "", "", 1, "longout", "set max number of try")

        self.lpv_curState = LocalPV(self.mod_name, self.fsm_name, "CUR-STATE", "", "", 40,  "waveform-text", "current state")
        self.lpv_fsmMsg   = LocalPV(self.mod_name, self.fsm_name, "FSM-MSG",   "", "", 128, "waveform-text", "FSM message")
        self.lpv_stayTime = LocalPV(self.mod_name, self.fsm_name, "STAY-TIME", "", "s", 1, "ai", "time after in this state")
        self.lpv_entryOK  = LocalPV(self.mod_name, self.fsm_name, "ENTRY-OK",  "", "",  1, "bi", "entry function exe OK")
        self.lpv_transOK  = LocalPV(self.mod_name, self.fsm_name, "TRANS-OK",  "", "",  1, "bi", "transit function exe OK")
        self.lpv_exitOK   = LocalPV(self.mod_name, self.fsm_name, "EXIT-OK",   "", "",  1, "bi", "exit function exe OK")
        self.lpv_running  = LocalPV(self.mod_name, self.fsm_name, "RUNNING",   "", "",  1, "bi", "FSM running or not")

        # variables for timer (will be started later)
        self.timer = RepeatedTimer(self.timer_intv, self._cb_timer)             # create the timer
        self.fsm_running = False                                                # indicate if the FSM is running or not

        # define the message queue
        self.msg_q = queue.Queue(1)                                             # message queue to comm with thread

    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    # post a message
    # ~~~~~~~~~~~~~~~~~~~~~~~~~       
    def postMsg(self, msg):
        msgStr  = time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime())
        msgStr += ' | ' + self.fsm_name + ': ' + msg
        print(msgStr)
        status = self.lpv_fsmMsg.write(msgStr)        

    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    # start the thread for FSM execution 
    # ~~~~~~~~~~~~~~~~~~~~~~~~~       
    def letGoing(self):
        # start the thread
        self.thrd = threading.Thread(target = self._thrd_func,
                                     args   = [],
                                     daemon = True,
                                     name   = "FSM-" + self.fsm_name)
        self.postMsg("Thread {} started.".format(self.thrd.name))
        self.thrd.start()

        # define the monitor PVs
        self.lpv_cmdStart.monitor(self._cb_cmd, [self.start])
        self.lpv_cmdStop.monitor (self._cb_cmd, [self.stop])
        self.lpv_cmdReset.monitor(self._cb_cmd, [self.reset])

    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    # start/stop/reset the FSM 
    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    def start(self):
        # start the timer if it is not running
        if not self.fsm_running:
            self.try_cnt_entry = 0
            self.try_cnt_trans = 0
            self.try_cnt_exit  = 0
            self.timer.reset()
            self.timer.start()
            self.fsm_running = True

            # send event to thread for displaying (avoid loop in pyEpics - see Note1)
            self.msg_q.put(['FSM started.', self.fsm_running])

    def stop(self, reason = 'user command'):
        self.timer.stop()
        self.fsm_running = False

        # Note: the stop will be also called by the _exe_fsm function, we use
        #       different implementation to avoid deadlock
        if reason == 'user command':                # from callback of EPICS
            self.msg_q.put(['FSM stopped by {}.'.format(reason), self.fsm_running])
        else:                                       # from local thread
            self.postMsg('FSM stopped by {}.'.format(reason))
            self.lpv_running.write(self.fsm_running)

    def reset(self):
        self.next_state     = self.states[0]
        self.current_state  = self.states[0]
        #self.last_state     = None

        self.entry_time     = time.time() 
        self.stay_time      = 0.0
        self.try_cnt_entry  = 0
        self.try_cnt_trans  = 0
        self.try_cnt_exit   = 0

        self.msg_q.put(['FSM reset.', self.fsm_running])

    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    # check if dt has passed after entering the state
    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    def after(self, dt):
        return self.stay_time >= dt

    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    # set init state
    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    def init_state(self, state_ini):        
        if state_ini in self.states:
            self.reset()
            self.next_state     = state_ini
            self.current_state  = state_ini
            self.last_state     = state_ini        
        else:
            self.postMsg('ERROR: state {} not in state list {}'.format(state_ini, self.states))

    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    # command PV callback
    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    def _cb_cmd(self, arg):
        fun = arg[0]            # the function to be executed
        cmd = arg[-1]           # the last component is the value of the monitored PV
        if cmd == 1:
            fun()

    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    # timer callback
    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    def _cb_timer(self):
        # send event to the thread
        self.msg_q.put([])

    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    # thread function
    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    def _thrd_func(self):
        # main loop
        while True:
            try: 
                msg = self.msg_q.get(timeout = self.timer_intv * 5)
                if len(msg) == 2:
                    self.postMsg(msg[0])
                    self.lpv_running.write(msg[1])
                else:
                    self._exe_fsm()
                self.msg_q.task_done()
            except queue.Empty:
                if self.mon_func is not None:
                    self.mon_func()
            except:
                print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                print("Exception in FSM execution:\n")
                excInfo = sys.exc_info()
                traceback.print_tb(excInfo[2])
                print(excInfo)
                print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")        

    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    # function to execute the FSM
    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    def _exe_fsm(self):
        # get the max try number
        mtry, _, _, status = self.lpv_setMaxTry.read(use_monitor = True)
        if status:
            if mtry >= 1 and mtry <= 10:
                self.max_try = mtry

        # --------------------
        # execute the entry if enter a new state
        # --------------------
        if self.current_state != self.last_state:
            # indicate the current state that we are working on
            self.lpv_curState.write(self.current_state)

            # execute the entry function
            if self.state_tr[self.current_state]['entry']:
                status = self.state_tr[self.current_state]['entry'](self.last_state)
                if not status:
                    self.try_cnt_entry += 1
                    self.postMsg('state {} entry() failed, try again...'.format(self.current_state))
                    if self.try_cnt_entry > self.max_try:
                        self.postMsg('state {} entry() failed, tried max {} times, stop!'.format(self.current_state, self.max_try))
                        self.stop(reason = '{} entry() failure'.format(self.current_state))
                    self.lpv_entryOK.write(False)
                    return
                else:
                    self.try_cnt_entry = 0                        
                        
            # remember the entry time and update the states
            self.entry_time = time.time()           # in second since the epoch of UTC
            self.last_state = self.current_state
            self.lpv_entryOK.write(True)

        # --------------------
        # update the stay time
        # --------------------
        self.stay_time = time.time() - self.entry_time
        self.lpv_stayTime.write(self.stay_time)

        # --------------------
        # perform transition (only when the last exit was correct, or
        #   this execution may be caused by the errors in exit function)
        # --------------------
        if (self.next_state == self.current_state) or (self.next_state is None):
            if self.state_tr[self.current_state]['transit']:
                self.next_state = self.state_tr[self.current_state]['transit']()
                if not self.next_state:
                    self.try_cnt_trans += 1
                    self.postMsg('state {} transit() failed, try again...'.format(self.current_state))
                    if self.try_cnt_trans > self.max_try:
                        self.postMsg('state {} transit() failed, tried max {} times, stop!'.format(self.current_state, self.max_try))
                        self.stop(reason = '{} transit() failure'.format(self.current_state))
                    self.lpv_transOK.write(False)
                    return
                else:
                    self.try_cnt_trans = 0
            else:
                self.next_state = self.current_state

            self.lpv_transOK.write(True)

        # --------------------
        # execute the exit if exit from a state
        # --------------------
        if self.next_state != self.current_state:
            # execute the exit function
            if self.state_tr[self.current_state]['exit']:
                status = self.state_tr[self.current_state]['exit'](self.next_state)
                if not status:
                    self.try_cnt_exit += 1
                    self.postMsg('state {} exit() failed, try again...'.format(self.current_state))
                    if self.try_cnt_exit > self.max_try:
                        self.postMsg('state {} exit() failed, tried max {} times, stop!'.format(self.current_state, self.max_try))
                        self.stop(reason = '{} exit() failure'.format(self.current_state))
                    self.lpv_exitOK.write(False)
                    return
                else:
                    self.try_cnt_exit = 0   
                    
            # update the states
            self.current_state = self.next_state
            self.lpv_exitOK.write(True)
                    





















