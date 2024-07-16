#####################################################################
#  Copyright (c) 2023 by Paul Scherrer Institute, Switzerland
#  All rights reserved.
#  Authors: Zheqiao Geng
#####################################################################
# Make file for the example

default: help
help ::
	@echo "Makefile for ooEpicsPy example"
	@echo "======================================================"
	@echo "available targets:"
	@echo " -> make clean       clean the Python compilation"
	@echo " -> make install     install the soft IOC"
	@echo "======================================================"

# remove all compiled data
clean ::
	rm -rf __pycache__	
	rm -rf cfg
	rm SGE-CPCL-RTEST1*
	
# install soft IOC
PYTHON3 := /opt/gfa/python-3.10/latest/bin/python

install ::
	$(PYTHON3) Install_SoftIOC.py


