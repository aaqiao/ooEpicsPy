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

from Softioc_Top import *

# define the soft IOC name
softIOCName = "SGE-CPCL-RTEST1"     # NOTE TO DESIGNER: change the soft IOC name to fit your soft IOC

# create object of the soft IOC
sIOC = Softioc_Top("SGE-RTEST1")    # NOTE TO DESIGNER: change the "module name" as first part of the local PV names (name space)
sIOC.genRunScript(softIOCName)

# generate the soft IOC
Application.generateSoftIOC(softIOCName, 
                            py_cmd = 'python',  # NOTE TO DESIGNER: change the python command as in your system
                            version = '1.0.0',
                            release_time = 'Jul. 16, 2024')

# copy the code to cfg folder, the execution home folder
os.system("cp *.py cfg/")           # copy all Python code to cfg/

# add your script below to install the soft IOC (including the ooEpicsPy code) 
# to your machine's installation location

