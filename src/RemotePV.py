#####################################################################
#  Copyright (c) 2023 by Paul Scherrer Institute, Switzerland
#  All rights reserved.
#  Authors: Zheqiao Geng
#####################################################################
# -------------------------------------------------
# Python based implementation of RemotePV using PyEpics
# -------------------------------------------------
import epics

class RemotePV:
    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    # class variables
    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    RPVList = []            # a list to collect all remote PVs

    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    # create the object
    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, pvName, local = False):
        # save the info               
        if pvName is None:
            self.pvName = ''
        else:
            self.pvName = pvName

        # add to list
        RemotePV.RPVList.append({"obj": self, "pvName": self.pvName, "local": local})

        # variables for object
        self.pv         = None      # object of epics.PV, be created later
        self.enable_mon = False     # indicate if the PV is monitored or not

    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    # create the PV object - will automatically connect
    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    def create(self):
        if self.pv is None:
            if (self.pvName != '') and (self.pvName != None):
                self.pv = epics.PV(self.pvName, connection_timeout = 1.0)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    # check connections tatus
    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    def is_connected(self):
        if self.pv is None:
            return False
        else:
            return (self.pv.status not in {None, 9, 10})  # see read() comments for status code meaning

    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    # read the value of the remote PV
    # CA status code: 
    #   use this command to check: epics.dbr.AlarmStatus(status).name
    #   0  :    NO_ALARM
    #   1  :    READ
    #   2  :    WRITE
    #   3  :    HIHI
    #   4  :    HIGH
    #   5  :    LOLO
    #   6  :    LOW
    #   7  :    STATE
    #   8  :    COS
    #   9  :    COMM
    #   10 :    TIMEOUT
    #   11 :    HW_LIMIT
    #   12 :    CALC
    #   13 :    SCAN
    #   14 :    LINK
    #   15 :    SOFT
    #   16 :    BAD_SUB
    #   17 :    UDF
    #   18 :    DISABLE
    #   19 :    SIMM                // simulaton mode
    #   20 :    READ_ACCESS
    #   21 :    WRITE_ACCESS
    #   None:   pv not exist (did not find by search)
    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    def read(self, return_str = False, use_monitor = False):
        # init the results
        results = [None, None, False, False]

        # get the data
        if self.pv:
            data = self.pv.get_with_metadata(form        = 'time',
                                             as_string   = return_str,
                                             use_monitor = self.enable_mon or use_monitor,
                                             timeout     = 1.0)
            if data is not None:
                results = [data['value'], 
                           data['timestamp'],
                           data['severity'] == 0,
                           data['status'] not in {9, 10, 18, 20}]
        
        # return the results
        return results
    
    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    # write value to the remote PV 
    # for MBBI or MBBO, must be the value, not the string
    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    def write(self, value, wait = False, timeout = 1.0):
        if self.pv:
            try:
                # pv.put return value: 1 for success, -1 on time-out
                # see: https://github.com/pyepics/pyepics/blob/master/epics/pv.py
                #      https://pyepics.github.io/pyepics/ca.html#epics.ca.put
                status = self.pv.put(value, wait = wait, timeout = timeout)
                return status == 1
            except:
                return False
        else:
            return False

    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    # monitor the remote PV   
    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    def monitor(self, cbFun = None, cbArgList = None):
        # remember the arg list
        if cbArgList: self.cbArgs = cbArgList.copy()
        else:         self.cbArgs = []
        self.cbArgs.append(0)                   # place holder for the value

        # local callback for the monitor
        def py_cb(pvname = None, value = None, char_value = None, **kw):
            if pvname == self.pvName:
                self.cbArgs[-1] = value
                if cbFun:
                    cbFun(self.cbArgs)

        # if PV object not created, create it
        self.create()

        # start the monitor by adding the callback function
        try:
            self.pv.add_callback(py_cb)
            self.enable_mon = True
        except:
            print('ERROR: failed to monitor PV ' + self.pvName)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    # open the PV - create PV objects for all RemotePVs (common function)         
    # ~~~~~~~~~~~~~~~~~~~~~~~~~   
    @classmethod
    def connect(cls):
        try:
            for pvConfig in cls.RPVList:
                pvConfig['obj'].create()
        except:
            print('ERROR: failed to create some of RemotePVs')

    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    # print all Remote PVs
    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    @classmethod
    def show(cls, local = False):
        # print the info: PV name, status, severity, value
        for pvConfig in cls.RPVList:
            dis_str = '{:50s}'.format(pvConfig['pvName'])
            pv      = pvConfig["obj"].pv

            # select the correct PV based on local == True/False
            if pv and (pvConfig["local"] == local):
                # get PV status and severity
                status   = pv.status
                severity = pv.severity

                # construct the info string
                if (status is None) or (severity is None):
                    dis_str += '{:18s}'.format("Not_Connected")
                    val = ''
                else:
                    # read the PV value
                    val, ts, alm, status = pvConfig["obj"].read()

                    # show the PV status
                    if status == 0:   dis_str += '{:8s}'.format("Normal")
                    else:             dis_str += '{:8s}'.format("Abnorm")
                    if severity == 0: dis_str += '{:10s}'.format("No_Alarm")
                    else:             dis_str += '{:10s}'.format("Alarm")

                print(dis_str + "  value = "+ str(val))

        
        
    
    
