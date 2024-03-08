#####################################################################
#  Copyright (c) 2023 by Paul Scherrer Institute, Switzerland
#  All rights reserved.
#  Authors: Zheqiao Geng
#####################################################################
# -------------------------------------------------
# Python based implementation of Application 
# -------------------------------------------------
import threading
import time
import os
import queue
import sys
import traceback

from RepeatedTimer import *
from LocalPV import *
from Job import *

# =================================
# function for the thread
# =================================
# main function of the thread
def AppThreadFunc(app):
    while True:
        try: 
            jobEnt = app.msgQ.get()
            job    = jobEnt[0]
            cmdId  = jobEnt[1]
            mutex  = jobEnt[2]

            if mutex is not None: mutex.acquire()
            job.execute(cmdId, None)
            if mutex is not None: mutex.release()

            app.msgQ.task_done()
        except:
            if mutex is not None:
                if mutex.locked(): mutex.release()

            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            print("Exception in job execution: " + jobEnt[0].jobName + "\n")
            excInfo = sys.exc_info()
            traceback.print_tb(excInfo[2])
            print(excInfo)
            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")
        
# callback function for commands executing jobs
def JobCmdCbFunc(cbArgs):
    app     = cbArgs[0]                     # object of the application
    job     = cbArgs[1]["job"]              # object of the job which command PV has changed
    cmdPV   = cbArgs[1]["cmd"]              # PV of the command
    cmdId   = cbArgs[1]["cid"]              # id of the command
    extCmd  = cbArgs[1]["extpv"]            # if it is external command or not
    mutex   = cbArgs[1]["mutex"]            # mutex for job execution
    cmdVal  = cbArgs[-1]                    # command PV value

    if extCmd:
        if app.msgQ.empty():                # if there is one command waiting, do not put new
            app.msgQ.put([job, cmdId, mutex])
    else:
        if cmdVal == 1:
            if not app.msgQ.full():
                app.msgQ.put([job, cmdId, mutex])

# callback function for timer-driven jobs
def RunPeriodicJob(job):
    job.execute(0, None)                    # execute the job, no subcommand supported

# =================================
# class for application 
# =================================
class Application:   
    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    # multiple applications will be install to the same soft IOC   
    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    softIOCName = ""
    appList     = [] 

    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    # create the object
    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, appName, modName):
        # save the input info 
        self.appName = appName
        self.modName = modName
        
        # create the list to store the jobs and command PVs
        self.jobList         = []       
        self.periodicJobList = []
                           
        # message queue
        self.msgQ = queue.Queue(2)

        # add to the application list
        Application.appList.append(self)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    # register a job object and create the command PV
    # ~~~~~~~~~~~~~~~~~~~~~~~~~       
    def registJob(self, job, cmdStr = "EXE", mutex = None):
        # check the input
        if not job:
            print("Failed to regist job!")
            return

        # there is only one command for the job
        if isinstance(cmdStr, str):
            self.jobList.append({"job": job,
                                 "cmd": LocalPV(self.modName,
                                                job.jobName,
                                                "CMD-"+cmdStr, 
                                                "",
                                                "",
                                                1,
                                                "bo",
                                                "command to execute job"),
                                 "cid": 0,
                                 "extpv": False,
                                 "mutex": mutex})

        # there are multiple commands for the job
        elif isinstance(cmdStr, list):
            cmdId = 0
            for cmd in cmdStr:               
                self.jobList.append({"job": job,
                                     "cmd": LocalPV(self.modName,
                                                    job.jobName,
                                                    "CMD-"+cmd,
                                                    "",
                                                    "",
                                                    1,
                                                    "bo",
                                                    "command to execute job"),
                                     "cid": cmdId,
                                     "extpv": False,
                                     "mutex": mutex})
                cmdId = cmdId + 1

    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    # register a job object with external trigger PV
    # ~~~~~~~~~~~~~~~~~~~~~~~~~       
    def registJobExtTrigPV(self, job, extPVList = [], mutex = None):
        # check the input
        if not job:
            print("Failed to register job with external trigger PV!")
            return
        
        if not isinstance(extPVList, list):
            print("Failed to register job with external trigger PV!")
            return

        cmdId = 0
        for extpv in extPVList:
            self.jobList.append({"job":   job,
                                 "cmd":   extpv,
                                 "cid":   cmdId,
                                 "extpv": True,
                                 "mutex": mutex})
            cmdId = cmdId + 1
                
    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    # register a job executed periodicly. This is a special case, 
    # the job will not be added to the list, but will be executed by a timer 
    # ~~~~~~~~~~~~~~~~~~~~~~~~~       
    def registJobPeriodic(self, job, period_s = 1.0):
        # check the input
        if not job:
            print("Failed to regist periodic job!")
            return

        # limit the period
        if period_s < 0.1:
            period_s = 1.0
        
        # save to list
        self.periodicJobList.append({"job":    job,
                                     "period": period_s,
                                     "timer":  None})       # timer is defined below

    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    # start the thread for job execution 
    # ~~~~~~~~~~~~~~~~~~~~~~~~~       
    def letGoing(self):
        # start the thread with trigger PVs
        if len(self.jobList) > 0:
            # start the thread for this application
            self.appThread = threading.Thread(target = AppThreadFunc,
                                              args   = (self,),
                                              daemon = True,
                                              name   = "TRD-" + self.appName)
            print("Thread " + self.appThread.name + " started.")
            self.appThread.start()

            # monitor the job command PVs
            for job_config in self.jobList:
                cbArgList = []
                cbArgList.append(self)
                cbArgList.append(job_config)
                job_config["cmd"].monitor(JobCmdCbFunc, cbArgList)
        
        # start the periodic timers
        if len(self.periodicJobList) > 0:
            for pjob in self.periodicJobList:
                pjob["timer"] = RepeatedTimer(pjob["period"], RunPeriodicJob, pjob["job"])
                pjob["timer"].start()
  
    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    # generate necessary files 
    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    @classmethod
    def generateSoftIOC(cls, softIOCName, py_cmd = 'python'):
        # file names
        cls.softIOCName = softIOCName
        cls.fileName_ss = softIOCName + "_startup.script"
        cls.fileName_db = softIOCName + ".template"
        cls.fileName_su = softIOCName + "_all.subs"
        cls.fileName_ex = softIOCName + "_run.py"

        print("Generate soft IOC " + softIOCName + "...\n")

        # create folders if they do not exist        
        if not os.path.exists("cfg"):
            os.mkdir("cfg")
            print("Folder cfg created\n")

        if not os.path.exists("gui"):
            os.mkdir("gui")
            print("Folder gui created\n")

        # create startup script for the soft IOC
        try:
            ssFile = open(cls.fileName_ss, "wt")    
        except IOError:
            print("Failed to created file " + cls.fileName_ss)
            return

        if py_cmd == '':
            py_cmd = 'python'
    
        ssFile.write("# -------------------------------------------\n")
        ssFile.write("# " + cls.fileName_ss + "\n")
        ssFile.write("# Auto created by ooPye, do not modify ...\n")
        ssFile.write("# -------------------------------------------\n\n")
        ssFile.write("# configure the environment\n")
        ssFile.write('epicsEnvSet "PYTHONPATH" "$(PWD)/cfg"\n\n')
        ssFile.write('epicsEnvSet "EPICS_CA_ADDR_LIST" "$(EPICS_CA_ADDR_LIST) localhost"\n\n')
        ssFile.write("# load records\n")
        ssFile.write('dbLoadRecords("' + cls.fileName_db + '", "")\n\n')
        ssFile.write("# init the IOC\n")
        ssFile.write("iocInit()\n\n")
        ssFile.write("# create the save/restore set\n")
        ssFile.write("< saveRestore.script_save\n\n")
        ssFile.write("# run the python engine\n")
        ssFile.write("cd cfg\n")
        ssFile.write('system "' + py_cmd + ' -i ' + cls.fileName_ex + '"\n')
        ssFile.write("\n")
        ssFile.close()

        print("File " + cls.fileName_ss + " created\n")

        # create the substitution file (it seems switsf needs it)
        try:
            suFile = open(cls.fileName_su, "wt")    
        except IOError:
            print("Failed to created file " + cls.fileName_su)
            return
        
        suFile.write("# -------------------------------------------\n")
        suFile.write("# " + cls.fileName_su + "\n")
        suFile.write("# Auto created by ooPye, do not modify ...\n")
        suFile.write("# -------------------------------------------\n\n")
        suFile.write("file " + cls.fileName_db)
        suFile.close()        

        # generate files used for the soft IOC
        LocalPV.gen_db      (cls.fileName_db)
        LocalPV.gen_srreq   ("cfg/" + cls.softIOCName + "_set.req")
        LocalPV.gen_arch    ("cfg/" + cls.softIOCName + ".config")
        
        print("Soft IOC " + softIOCName + " generation done!\n")
        
# =================================
# exit function
# =================================
def exit():
    for app in Application.appList:
        for tm in app.periodicJobList:
            if not tm["timer"] == None:
                tm["timer"].stop()
    sys.exit()

def quit():
    exit()




