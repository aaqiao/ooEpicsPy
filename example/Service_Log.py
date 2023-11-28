#####################################################################
#  Copyright (c) 2023 by Paul Scherrer Institute, Switzerland
#  All rights reserved.
#  Authors: Zheqiao Geng
#####################################################################
#################################################################
# The message logger 
#################################################################
import time
from LocalPV import *

# =================================
# define the class
# =================================
class Service_Log:
    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    # class variables
    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    MAX_MSG_NUM = 100
    MAX_MSG_LEN = 110

    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    # create the object
    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, modName, prefixStr):
        # remember
        self.modName    = modName
        self.prefixStr  = prefixStr

        self.strBuf     = ""                # big buffer
        self.strBufList = []                # ring buffer
        self.strHead    = 0   

        for i in range(Service_Log.MAX_MSG_NUM):
            self.strBufList.append("")

        # define local PVs
        self.lpv_monLogMsg = LocalPV(self.modName, "LOG", "MON-MSG", "", "", \
            Service_Log.MAX_MSG_NUM * Service_Log.MAX_MSG_LEN, "waveform-text", "Run-time messages")

    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    # post a message
    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    def postMessage(self, prefix, severity, msg):
        # make up the message string
        msgStr  = time.strftime("[%Y-%m-%d %H:%M:%S] ", time.localtime())
        msgStr += self.prefixStr
        msgStr += "|"
        msgStr += severity
        msgStr += ": "
        msgStr += prefix
        msgStr += ": "
        msgStr += msg

        # put the string to buffer (limit the length)
        self.strBufList[self.strHead]  = msgStr[:Service_Log.MAX_MSG_LEN-1]
        self.strBufList[self.strHead] += '\n'

        print(self.strBufList[self.strHead])
        
        # update the head, which is the place that will be written next time
        self.strHead += 1
        if self.strHead >= Service_Log.MAX_MSG_NUM:
            self.strHead = 0

        # put to the big buffer
        self.strBuf = ""

        curId = self.strHead

        for i in range(Service_Log.MAX_MSG_NUM):
            # get the id of string
            curId -= 1
            if curId < 0:
                curId = Service_Log.MAX_MSG_NUM - 1

            # put to the big string
            self.strBuf += self.strBufList[curId]

        # put the string to PV
        self.lpv_monLogMsg.write(self.strBuf)


        













