#####################################################################
#  Copyright (c) 2023 by Paul Scherrer Institute, Switzerland
#  All rights reserved.
#  Authors: Zheqiao Geng
#####################################################################
#################################################################
# Example job to execute iteratively
#################################################################
from ooepics.Job import *

class Job_Iterative(Job):
    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    # create the object
    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, modName, jobName):
        # init the parent class
        Job.__init__(self, modName, jobName)

        # create local PVs
        self.lpv_monHeartBeat = LocalPV(self.modName, self.jobName, "MON-HEART-BEAT", "", "", 1, "bi", "heart beat")

        # values
        self.lpv_heartBeatVal = 0

    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    # execute the job  
    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    def execute(self, cmdId, dataBus):
        if self.lpv_heartBeatVal == 0:
            self.lpv_heartBeatVal = 1
        else:
            self.lpv_heartBeatVal = 0

        self.lpv_monHeartBeat.write(self.lpv_heartBeatVal)


   





