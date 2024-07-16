#####################################################################
#  Copyright (c) 2023 by Paul Scherrer Institute, Switzerland
#  All rights reserved.
#  Authors: Zheqiao Geng
#####################################################################
# Makefile for ooEpicsPy

default: help
help ::
	@echo "Makefile for ooEpicsPy"
	@echo "======================================================"
	@echo "available targets:"
	@echo " -> make clean       clean the Python compilation"
	@echo "======================================================"

# remove all compiled data
clean ::
	rm -rf __pycache__
	rm -rf ooepics/__pycache__
	make clean -C example
