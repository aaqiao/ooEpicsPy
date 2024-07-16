#!/bin/bash
#####################################################################
#  Copyright (c) 2023 by Paul Scherrer Institute, Switzerland
#  All rights reserved.
#  Authors: Zheqiao Geng
#####################################################################

#caqtdm="/mnt/c/Program Files/caQTDM/bin/windows-x64/caQtDM.exe"
ModuleName=SGE-RTEST1

echo "Start panels for ooPye example"
declare -x EPICS_CA_ADDR_LIST="$EPICS_CA_ADDR_LIST localhost"

#"$caqtdm" -macro "MODULE_NAME=$ModuleName" GUI_example.ui &
caqtdm -macro "MODULE_NAME=$ModuleName" GUI_example.ui &

