#####################################################################
#  Copyright (c) 2023 by Paul Scherrer Institute, Switzerland
#  All rights reserved.
#  Authors: Zheqiao Geng
#####################################################################
#################################################################
# An example FSM emulating the traffic light
#################################################################
from FSMLite import *

# =================================
# define the class
# =================================
class FSM_TrafficLight():
    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    # create the object
    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, modName, fsmName, srvLog):
        # init the parent class
        self.modName = modName
        self.fsmName = fsmName
        self.srv_Log = srvLog

        # define local PVs, PV names will be built up as: $(module_name)-$(job_name):$(data_name)
        #   parameters:
        #       module name; 
        #       job name; 
        #       data name; 
        #       selection string list (for mbbi/mbbo); 
        #       number of element; 
        #       record type; 
        #       description      
        self.lpv_redLight    = LocalPV(self.modName, self.fsmName, "RED",    "", "",  1, "bi", "red light on/off")
        self.lpv_greenLight  = LocalPV(self.modName, self.fsmName, "GREEN",  "", "",  1, "bi", "green light on/off")
        self.lpv_yellowLight = LocalPV(self.modName, self.fsmName, "YELLOW", "", "",  1, "bi", "yellow light on/off")
        
        # define the state and the state transition
        self.states = ['red', 'green', 'yellow']

        self.state_tr = {}
        self.state_tr['red']     = {'entry': self.entry_red,    'exit': self.exit_red,    'transit': self.transit_red}
        self.state_tr['green']   = {'entry': self.entry_green,  'exit': self.exit_green,  'transit': self.transit_green}
        self.state_tr['yellow']  = {'entry': self.entry_yellow, 'exit': self.exit_yellow, 'transit': self.transit_yellow}        

        self.fsm = FSMLite( mod_name    = self.modName,     # module name, for constructing PV names
                            fsm_name    = self.fsmName,     # FSM name, for constructing PV names
                            timer_intv  = 1,                # time interval of the timer driving FSM
                            states      = self.states,      # list of states
                            state_tr    = self.state_tr)    # state transition dict

    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    # start the FSM
    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    def letGoing(self):
        self.fsm.letGoing()

    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    # functions for state 'red'
    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    def entry_red(self, state_from):
        s1 = self.lpv_redLight.write     (True)
        s2 = self.lpv_greenLight.write   (False)
        s3 = self.lpv_yellowLight.write  (False)
        print('red entry')
        return all([s1, s2, s3])
        
    def exit_red(self, state_to):
        print('red exit')
        return True

    def transit_red(self):
        print('red transit')
        if self.fsm.after(3):
            return 'yellow'
        else:
            return 'red'

    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    # functions for state 'yellow'
    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    def entry_yellow(self, state_from):
        s1 = self.lpv_redLight.write     (False)
        s2 = self.lpv_greenLight.write   (False)
        s3 = self.lpv_yellowLight.write  (True)

        self.come_from = state_from                 # remember the last state before enter
        print('yello entry')
        return all([s1, s2, s3])
        
    def exit_yellow(self, state_to):
        print('yello exit')
        return True

    def transit_yellow(self):
        print('yello transit')
        if self.fsm.after(1 if self.come_from == 'red' else 3):
            return 'green' if self.come_from == 'red' else 'red'
        else:
            return 'yellow'

    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    # functions for state 'green'
    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    def entry_green(self, state_from):
        s1 = self.lpv_redLight.write     (False)
        s2 = self.lpv_greenLight.write   (True)
        s3 = self.lpv_yellowLight.write  (False)
        print('green entry')
        return all([s1, s2, s3])
        
    def exit_green(self, state_to):
        print('green exit')
        return True

    def transit_green(self):
        print('green transit')
        if self.fsm.after(10):
            return 'yellow'
        else:
            return 'green'




