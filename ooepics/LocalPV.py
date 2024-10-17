#####################################################################
#  Copyright (c) 2023 by Paul Scherrer Institute, Switzerland
#  All rights reserved.
#  Authors: Zheqiao Geng
#####################################################################
# -------------------------------------------------
# Python based implementation of LocalPV
# -------------------------------------------------
from ooepics.RecordTemplate import generateRecord
from ooepics.RemotePV import *

class LocalPV:
    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    # class variables
    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    LPVList  = []                   # a list to collect all local PVs
    LPVTypes = {"ao",               # PV types supported
                "ai",
                "bo",
                "bi",
                "mbbo",
                "mbbi",
                "longin",
                "longout",
                "stringin",
                "stringout",
                "waveform",
                "waveform-text"}

    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    # create the object
    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, modStr, devStr, valStr, selItems, unitStr, pno, recTypeStr, descStr, enaSR = True):
        # save the input info 
        self.modName    = modStr                # module name
        self.devName    = devStr                # device name
        self.valName    = valStr                # value name
        self.selItems   = selItems              # items for mbbi or mbbo records
        self.unitStr    = unitStr               # string of unit
        self.pointNum   = pno                   # number of point
        self.recordType = recTypeStr            # record type
        self.descStr    = descStr               # record description
        self.enaSR      = enaSR                 # True to enable save/restore
        
        # check the input 
        if self.recordType not in LocalPV.LPVTypes:
            print("ERROR: LocalPV record type {} not supported!".format(self.recordType))
            return
        
        # derive the full PV name
        if self.devName: self.pvName = self.modName + "-" + self.devName + ":" + self.valName
        else:            self.pvName = self.modName + ":" + self.valName
        
        # save to the global list 
        LocalPV.LPVList.append({"obj":          self,
                                "pvName":       self.pvName,
                                "selItems":     self.selItems,
                                "unitStr":      self.unitStr, 
                                "pointNum":     self.pointNum, 
                                "recordType":   self.recordType,
                                "descStr":      self.descStr,
                                "enaSR":        self.enaSR})   
            
        # variables for object
        self.pv = RemotePV(self.pvName, local = True)   # we use RemotePV to access local PV

    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    # read the value of the local PV   
    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    def read(self, return_str = False, use_monitor = False):
        return self.pv.read(return_str = return_str, use_monitor = use_monitor)
    
    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    # write value to the local PV   
    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    def write(self, value, wait = False, timeout = 1.0):
        return self.pv.write(value, wait = wait, timeout = timeout)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    # monitor the local PV   
    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    def monitor(self, cbFun = None, cbArgList = None):
        self.pv.monitor(cbFun, cbArgList = cbArgList)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    # print all local PVs
    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    @classmethod
    def show(cls):
        RemotePV.show(local = True)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    # init waveform PV (common function)         
    # ~~~~~~~~~~~~~~~~~~~~~~~~~                
    @classmethod
    def init_wfs(cls):
        for pvConfig in cls.LPVList:
            if pvConfig["recordType"] == "waveform":
                pvConfig["obj"].write([0] * pvConfig["pointNum"])

    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    # generate EPICS database file
    # ~~~~~~~~~~~~~~~~~~~~~~~~~   
    @classmethod
    def gen_db(cls, fileName):
        # open the file
        try:
            dbFile = open(fileName, "wt")    
        except IOError:
            print("Failed to created file " + fileName)
            return
    
        # write the title
        dbFile.write("# -------------------------------------------\n")
        dbFile.write("# " + fileName + "\n")
        dbFile.write("# Auto created by ooPye, do not modify ...\n")
        dbFile.write("# -------------------------------------------\n\n")
        
        # write the PV definitions
        for pvConfig in cls.LPVList:
            pvStr = generateRecord( pvConfig['pvName'],
                                    pvConfig['selItems'],
                                    pvConfig['unitStr'],
                                    pvConfig['pointNum'],
                                    pvConfig['recordType'],
                                    pvConfig['descStr'])
            dbFile.write(pvStr)
            
        dbFile.close()       
        print("File " + fileName + " created\n")

    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    # generate save restore request file
    # ~~~~~~~~~~~~~~~~~~~~~~~~~   
    @classmethod
    def gen_srreq(cls, fileName):
        # open the file
        try:
            srFile = open(fileName, "wt")    
        except IOError:
            print("Failed to created file " + fileName)
            return
    
        # write the title
        srFile.write("#//UPDATE-FREQ=10\n")
        srFile.write("#ENABLE-PASS=1\n")
        srFile.write("# -------------------------------------------\n")
        srFile.write("# " + fileName + "\n")
        srFile.write("# Auto created by ooPye, do not modify ...\n")
        srFile.write("# -------------------------------------------\n\n")
        
        # write the PV definitions
        for pvConfig in cls.LPVList:
            if pvConfig['enaSR']:
                if pvConfig['recordType'] in {"ao", "longout"}:
                    srFile.write(pvConfig['pvName'] + "\n")
                    srFile.write(pvConfig['pvName'] + ".HIHI\n")
                    srFile.write(pvConfig['pvName'] + ".HIGH\n")
                    srFile.write(pvConfig['pvName'] + ".LOW\n")
                    srFile.write(pvConfig['pvName'] + ".LOLO\n")
                    srFile.write(pvConfig['pvName'] + ".DRVL\n")
                    srFile.write(pvConfig['pvName'] + ".DRVH\n")
                    srFile.write(pvConfig['pvName'] + ".LSV\n")
                    srFile.write(pvConfig['pvName'] + ".HSV\n")

                if pvConfig['recordType'] in {"ai", "longin"}:
                    srFile.write(pvConfig['pvName'] + ".HIHI\n")
                    srFile.write(pvConfig['pvName'] + ".HIGH\n")
                    srFile.write(pvConfig['pvName'] + ".LOW\n")
                    srFile.write(pvConfig['pvName'] + ".LOLO\n")
                    srFile.write(pvConfig['pvName'] + ".LSV\n")
                    srFile.write(pvConfig['pvName'] + ".HSV\n")

                if pvConfig['recordType'] in {"bo", "mbbo", "waveform", "stringout"}:
                    srFile.write(pvConfig['pvName'] + "\n")
           
        srFile.close()
        
        print("File " + fileName + " created\n")
        pass
        
    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    # generate archiver configuration file
    # ~~~~~~~~~~~~~~~~~~~~~~~~~   
    @classmethod
    def gen_arch(cls, fileName):
        pass
        
        
    
    
