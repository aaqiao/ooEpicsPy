#####################################################################
#  Copyright (c) 2023 by Paul Scherrer Institute, Switzerland
#  All rights reserved.
#  Authors: Zheqiao Geng
#####################################################################
# -------------------------------------------------
# Timer implementation
# -------------------------------------------------
from threading import Timer

# =================================
# class definition
# =================================
class RepeatedTimer():
    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    # define the timer
    # ~~~~~~~~~~~~~~~~~~~~~~~~~  
    def __init__(self, interval, user_cb, *args, **kwargs):
        # save the input
        self.interval   = interval if interval >= 0.1 else 1
        self.user_cb    = user_cb
        self.args       = args
        self.kwargs     = kwargs

        # define the object and variables
        self.cmd_stop       = False         # indicate stop command received
        self.timer_waiting  = False         # indicate if the timer is in waiting stage
        self.timer          = None          # object of the timer

    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    # callback function
    # ~~~~~~~~~~~~~~~~~~~~~~~~~  
    def _timer_cb(self):
        # when callback is called, means timer fired
        self.timer_waiting = False

        # execute the callback function
        if self.user_cb:
            self.user_cb(*self.args, **self.kwargs)

        # re-call the start function
        if not self.cmd_stop:
            self.start()

    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    # start the timer
    # note: the "Timer" object only run once and the object will be discarded, 
    #       we need to repeat defining new Timer object to continue. In this 
    #       case, the timer is natrally only started after the user callback
    #       function is finished (as in the _timer_cb routine)
    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    def start(self, new_intv = None):
        # possibly update the interval
        if new_intv is not None:
            self.interval = new_intv if new_intv > 1.0e-6 else 1.0

        # re-arm the timer
        if not self.timer_waiting:
            self.timer_waiting = True
            self.timer         = Timer(self.interval, self._timer_cb)
            self.timer.start()

    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    # stop the repeated timer
    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    def stop(self):
        # stop the timer, and cancel the execution of the timer’s action. 
        # this will only work if the timer is still in its waiting stage.
        if self.timer:
            self.timer.cancel()
            self.timer_waiting = False

        # be sure the timer will be stopped
        self.cmd_stop = True

    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    # reset the timer after stop
    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    def reset(self):
        # clear the stop command
        self.cmd_stop = False






























