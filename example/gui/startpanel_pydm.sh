#!/bin/bash
#####################################################################
#  Copyright (c) 2023 by Paul Scherrer Institute, Switzerland
#  All rights reserved.
#  Authors: Zheqiao Geng
#####################################################################

echo "Start panels for ooPye example"
#declare -x EPICS_CA_ADDR_LIST="$EPICS_CA_ADDR_LIST localhost"

pydm -m '{"MODULE_NAME":"SGE-RTEST1","SIOC_NAME":"SGE-CPCL-RTEST1"}' --hide-nav-bar GUI_example_pydm.ui &


