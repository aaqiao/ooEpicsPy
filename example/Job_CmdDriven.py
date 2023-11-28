#####################################################################
#  Copyright (c) 2023 by Paul Scherrer Institute, Switzerland
#  All rights reserved.
#  Authors: Zheqiao Geng
#####################################################################
#################################################################
# An example job that is driven by commands
#################################################################
import time

from Job import *
from Service_RFStation import *

# =================================
# define the class
# =================================
class Job_CmdDriven(Job):
    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    # create the object
    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, modName, jobName, srvLog, srvRF1, srvRF2):
        # init the parent class
        Job.__init__(self, modName, jobName)
        self.srv_Log = srvLog
        self.srv_rf1 = srvRF1
        self.srv_rf2 = srvRF2

        # define local PVs, PV names will be built up as: $(module_name)-$(job_name):$(data_name)
        #   parameters:
        #       module name; 
        #       job name; 
        #       data name; 
        #       selection string list (for mbbi/mbbo); 
        #       number of element; 
        #       record type; 
        #       description
        
        items_compare = ("Station 1", "Station 2", "Equal")  

        self.lpv_monWf1         = LocalPV(self.modName, self.jobName, "MON-WF1",                "", "dig", 2048, "waveform", "display waveform from RF station 1")
        self.lpv_monWf2         = LocalPV(self.modName, self.jobName, "MON-WF2",                "", "dig", 2048, "waveform", "display waveform from RF station 2")
        self.lpv_monWfTime      = LocalPV(self.modName, self.jobName, "MON-TIME-X",             "", "us",  2048, "waveform", "time axis for x")

        self.lpv_monAccVolt1    = LocalPV(self.modName, self.jobName, "MON-ACC-VOLT1",          "", "MV",  1, "ai",   "acc volt of RF station 1")
        self.lpv_monAccVolt2    = LocalPV(self.modName, self.jobName, "MON-ACC-VOLT2",          "", "MV",  1, "ai",   "acc volt of RF station 2")
        self.lpv_monLarger      = LocalPV(self.modName, self.jobName, "MON-LARGER",  items_compare, "",    1, "mbbi", "display which acc volt larger")

        self.lpv_setPhase_deg   = LocalPV(self.modName, self.jobName, "SET-PHASE-ALL",          "", "deg", 1, "ao",   "set beam phase to both stations")

        # message
        self.srv_Log.postMessage(self.clsname+"::__init__()", "INFO", "inst. " + jobName + " created.")

    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    # execute the job  
    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    def execute(self, cmdId, dataBus):
        # check the RF stations
        if not isinstance(self.srv_rf1, Service_RFStation) or \
           not isinstance(self.srv_rf2, Service_RFStation):
            self.srv_Log.postMessage(self.clsname+"::execute()", "ERROR", "Invalid RF station services!")
            return [dataBus, False]

        # response to command: GET-WAVEFORM
        if cmdId == 0:
            # read the waveforms
            wf1, wfTime, status1 = self.srv_rf1.getWaveform()
            wf2, wfTime, status2 = self.srv_rf2.getWaveform()

            # save to local PVs
            if (not status1) and (not status2):
                self.srv_Log.postMessage(self.clsname+"::execute()", "ERROR", "Failed to get waveforms!")
                return [dataBus, False]
            elif status1 and (not status2):
                self.srv_Log.postMessage(self.clsname+"::execute()", "WARN", "Only get waveform from station 1!")
                self.lpv_monWf1.write(wf1)
            elif (not status1) and status2:
                self.srv_Log.postMessage(self.clsname+"::execute()", "WARN", "Only get waveform from station 2!")
                self.lpv_monWf2.write(wf2)
            else:
                self.srv_Log.postMessage(self.clsname+"::execute()", "INFO", "Sucessfully get waveforms")
                self.lpv_monWf1.write(wf1)
                self.lpv_monWf2.write(wf2)

            self.lpv_monWfTime.write(wfTime)
            return [dataBus, True]

        # response to command: COMPARE-ACC-VOLT
        elif cmdId == 1:
            # read the values
            accVolt1, status1 = self.srv_rf1.getAccVolt()
            accVolt2, status2 = self.srv_rf2.getAccVolt()

            if (not status1) or (not status2):
                self.srv_Log.postMessage(self.clsname+"::execute()", "ERROR", "Not able to get acc volts from both stations!")
                return [dataBus, False]

            # save to local PVs
            self.lpv_monAccVolt1.write(accVolt1)
            self.lpv_monAccVolt2.write(accVolt2)

            if accVolt1 > accVolt2:
                self.lpv_monLarger.write(0)
            elif accVolt1 < accVolt2:
                self.lpv_monLarger.write(1)
            else:
                self.lpv_monLarger.write(2)                
                
            self.srv_Log.postMessage(self.clsname+"::execute()", "INFO", "Acc volt comparision successful")
            return [dataBus, True]

        # response to command: SET-PHASE-SP
        elif cmdId == 2:
            # get the local PV setting
            [beamPhaseSP, timestamp, alarmsev, status] = self.lpv_setPhase_deg.read()
            if not status:
                self.srv_Log.postMessage(self.clsname+"::execute()", "ERROR", "Failed to get the beam phase local setting!")
                return [dataBus, False]

            # set the phase to the two stations           
            status1 = self.srv_rf1.setBeamPhase(beamPhaseSP)
            status2 = self.srv_rf2.setBeamPhase(beamPhaseSP)
            
            if (not status1) and (not status2):
                self.srv_Log.postMessage(self.clsname+"::execute()", "ERROR", "Failed to set beam phase to both stations!")
                return [dataBus, False]
            elif status1 and (not status2):
                self.srv_Log.postMessage(self.clsname+"::execute()", "WARN", "Only set beam phase for station 1!")
            elif (not status1) and status2:
                self.srv_Log.postMessage(self.clsname+"::execute()", "WARN", "Only set beam phase for station 2!")
            else:
                self.srv_Log.postMessage(self.clsname+"::execute()", "INFO", "Sucessfully set beam phase to both stations")

            return [dataBus, True]

        # unkown commands
        else:
            self.srv_Log.postMessage(self.clsname+"::execute()", "ERROR", "Command not known!")
            return [dataBus, False]
















