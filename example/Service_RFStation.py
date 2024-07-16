#####################################################################
#  Copyright (c) 2023 by Paul Scherrer Institute, Switzerland
#  All rights reserved.
#  Authors: Zheqiao Geng
#####################################################################
#################################################################
# This is an example service to interact with the LLRF system 
# of an RF station
#################################################################
import time
import numpy as np

from ooepics.RemotePV import *

# =================================
# class of service for RF station interaction
# =================================
class Service_RFStation:
    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    # class variables
    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    # remote PV names
    RPVADDR = { "get_amplt_wf_load100"  : "SIG-AMPLT",      \
                "get_time_x"            : "TIME-AXIS",      \
                "get_acc_volt"          : "GET-ACC-VOLT",   \
                "set_beam_phase"        : "SET-BEAM-PHASE"}

    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    # create the object
    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, modName, srvName, rfStation):
        # save the names
        self.modName    = modName
        self.srvName    = srvName
        self.rfStation  = rfStation

        # create the remote PVs
        self.rpvs = {}
        for pvk in Service_RFStation.RPVADDR.keys():
            self.rpvs[pvk] = RemotePV(self.rfStation + "-" + Service_RFStation.RPVADDR[pvk])

        print("Service_RFStation::__init__(): INFO: inst. " + srvName + " created for module " + modName)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    # get the waveform 
    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    def getWaveform(self):
        #[waveformValue, timestamp1, alarmSev1, status1] = self.rpvs["get_amplt_wf_load100"].read()
        #[waveformTime,  timestamp2, alarmSev2, status2] = self.rpvs["get_time_x"].read()
        waveformValue = np.random.randn(2048)
        waveformTime  = np.arange(2048) * 1.0e-6
        status1 = status2 = True
        return [waveformValue, waveformTime, (status1 and status2)]

    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    # get the acc voltage 
    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    def getAccVolt(self):
        #[accVolt, timestamp, alarmSev, status] = self.rpvs["get_acc_volt"].read()
        accVolt = np.random.randn(1)[0]
        status  = True
        return [accVolt, status]

    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    # set the phase
    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    def setBeamPhase(self, phase):
        # set the phase
        #status = self.rpvs["set_beam_phase"].write(phase)
        print('Set the phase to ', phase)
        status = True
        return status


