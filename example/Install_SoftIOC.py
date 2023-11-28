#####################################################################
#  Copyright (c) 2023 by Paul Scherrer Institute, Switzerland
#  All rights reserved.
#  Authors: Zheqiao Geng
#####################################################################
#################################################################
# Install a soft ioc
#################################################################
import os
import sys

sys.path.append("../src/")                      # NOTE TO DESIGNER: point to where ooEpicsPy files are stored

from Softioc_Top import *

# define the soft IOC name
softIOCName = "SGE-CPCL-RTEST1"                 # NOTE TO DESIGNER: change the soft IOC name to fit your soft IOC

# create object of the soft IOC
sIOC = Softioc_Top("SGE-RTEST1")                # NOTE TO DESIGNER: change the "module name" as first part of the local PV names (name space)
sIOC.genRunScript(softIOCName)

# generate the soft IOC
Application.generateSoftIOC(softIOCName, 
                            py_cmd = 'python3') # NOTE TO DESIGNER: change the python command as in your system

# copy the code to cfg folder, the execution home folder
os.system("cp ../src/*.py cfg")                 # copy the ooEpicsPy files to cfg/
os.system("cp *.py cfg/")                       # copy all Python code to cfg/

# add your script below to install the soft IOC (including the ooEpicsPy code) 
# to your machine's installation location

