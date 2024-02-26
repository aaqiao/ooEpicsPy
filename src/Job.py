#####################################################################
#  Copyright (c) 2023 by Paul Scherrer Institute, Switzerland
#  All rights reserved.
#  Authors: Zheqiao Geng
#####################################################################
# -------------------------------------------------
# Python based implementation of Job. This is a base class 
# -------------------------------------------------
import time
from LocalPV import *

class Job:    
    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    # class variable
    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    EXE     = 0             # execute the functions
    NOEXE   = 1             # no execution

    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    # create the object
    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, modName, jobName):
        # save the input info 
        self.modName    = modName
        self.jobName    = jobName
        self.clsname    = self.__class__.__name__
            
    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    # execute the job, this should be implemented in the derived class  
    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    def execute(self, cmdId = 0, dataBus = None):
        print("Job " + self.jobName + str(cmdId) + " for app " + self.modName + " executed!")
        return True

        
