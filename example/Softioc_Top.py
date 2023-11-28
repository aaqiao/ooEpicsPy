#####################################################################
#  Copyright (c) 2023 by Paul Scherrer Institute, Switzerland
#  All rights reserved.
#  Authors: Zheqiao Geng
#####################################################################
#################################################################
# The top structure for the soft IOC
#################################################################
from Application import *

from Job_CmdDriven import *
from Job_Iterative import *
from FSM_TrafficLight import *
from Service_RFStation import *
from Service_Log import *

# =================================
# assemble the soft IOC
# =================================
class Softioc_Top:
    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    # create the object
    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, moduleName):
        # remember input
        self.moduleName = moduleName            # "moduleName" is the first part of the local PV names

        # --------
        # define an application - the run coordinator
        # --------
        #   parameters : 
        #       1st: application name, define the thread name by adding "TRD-" before it
        #       2ed: module name, used to define local PV names
        self.appTest = Application("APPTST", self.moduleName)

        # --------
        # define the services
        # --------
        #   parameters:
        #       1st: module name, used to define local PV names
        #       2ed: prefix of the messages
        self.srvLog         = Service_Log           (self.moduleName, "TSTMSG ")

        #   parameters:
        #       1st: module name, used to define local PV names
        #       2ed: service name
        #       3rd: string passing to the service object to build up the remote PV names
        self.srvRFStation1  = Service_RFStation     (self.moduleName, "SRVL201", "S20CB01")
        self.srvRFStation2  = Service_RFStation     (self.moduleName, "SRVL202", "S20CB02")

        # --------
        # define the jobs
        # --------
        #   parameters:
        #       1st: module name, used to define local PV names
        #       2ed: job name, used to define local PV names
        #       3rd: object of service for run-time message log
        #       4,5th: objects of RF station services for two stations
        self.jobCmdDriven   = Job_CmdDriven         (self.moduleName, "JOBCMDD", self.srvLog, self.srvRFStation1, self.srvRFStation2)
        self.jobIterative   = Job_Iterative         (self.moduleName, "JOBITER")

        # --------
        # register jobs to the application
        # --------
        #   parameters:
        #       1st: the object of a job
        #       2ed: commands that the job needs to handle, the string will appear in the command PV name
        self.appTest.registJob          (self.jobCmdDriven, ["GET-WAVEFORM", "COMPARE-ACC-VOLT", "SET-PHASE-SP"])

        #   parameters:
        #       1st: the object of a job
        #       2ed: period of the iterative execution, second
        self.appTest.registJobPeriodic  (self.jobIterative, 1)

        # --------
        # define the FSMs
        # --------
        #   parameters:
        #       1st: module name, used to define local PV names
        #       2ed: FSM name, used to define local PV names
        #       3rd: object of service for run-time message log
        self.fsmTrafficLight = FSM_TrafficLight(self.moduleName, "FSMTLGT", self.srvLog)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    # run the soft IOC thread
    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    def run(self):
        self.appTest.letGoing()             # each application is driven by a thread
        self.fsmTrafficLight.letGoing()     # each FSM is driven by a thread

    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    # generate the run script
    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    def genRunScript(self, softIOCName):
        # remember
        self.softIOCName = softIOCName
        fullFileName     = softIOCName + "_run.py"

        # create the file
        try:
            ssFile = open(fullFileName, "wt")    
        except IOError:
            print("Failed to created file " + fullFileName)
            return
    
        ssFile.write("# -------------------------------------------\n")
        ssFile.write("# " + fullFileName + "\n")
        ssFile.write("# Auto created by Softioc_Top, do not modify\n")
        ssFile.write("# -------------------------------------------\n")
        ssFile.write("from Softioc_Top import *\n\n")

        ssFile.write("# configure the environment\n")
        ssFile.write('sIOC = Softioc_Top("' + self.moduleName + '")\n\n')

        ssFile.write("# connect to all PVs\n")
        ssFile.write("RemotePV.connect()\n\n")
        ssFile.write("# run the soft ioc\n")
        ssFile.write("sIOC.run()\n\n")





