#####################################################################
#  Copyright (c) 2023 by Paul Scherrer Institute, Switzerland
#  All rights reserved.
#  Authors: Zheqiao Geng
#####################################################################
# -------------------------------------------------
# Template of records
# -------------------------------------------------

# ~~~~~~~~~~~~~~~~~~~~~~~~~
# generate a record string. The record type support:
# ao, ai, bo, bi, mbbo, mbbi, longin, longout, stringin, stringout, waveform
# ~~~~~~~~~~~~~~~~~~~~~~~~~
def generateRecord(pvName, selItems, unitStr, pointNum, recordType, descStr):
    recStr = '';
    
    # special treat the record type string
    recordTypeStr = recordType    

    if recordType in {'waveform-text'}:
        recordTypeStr = "waveform"

    # insert the common lines for a record
    recStr = recStr + 'record(' + recordTypeStr + ', "' + pvName + '") {\n'
    recStr = recStr + '    field(DESC, "' + descStr + '")\n'
    recStr = recStr + '    field(SCAN, "Passive")\n'
    
    # specific field for ao, ai, longin, longout and waveform
    if recordType in {'ao', 'ai', 'longin', 'longout', 'waveform'}:
        recStr = recStr + '    field(EGU,  "' + unitStr + '")\n'
    
    # specific field for ao and ai
    if recordType in {'ao', 'ai'}:
        recStr = recStr + '    field(PREC, "3")\n'
    
    # specific field for bi
    if recordType in {'bi'}:
        recStr = recStr + '    field(OSV, "NO_ALARM")\n'
        recStr = recStr + '    field(ZSV, "MAJOR")\n'
        
    # specific field for mbbo or mbbi
    selFields = ('ZRST', 'ONST', 'TWST', 'THST', 'FRST', 'FVST', \
        'SXST', 'SVST', 'EIST', 'NIST', 'TEST', 'ELST', 'TVST', \
        'TTST', 'FTST', 'FFST')
    
    if recordType in {'mbbo', 'mbbi'}:
        for fieldStr, itemStr in zip(selFields, selItems):
            recStr = recStr + '    field(' + fieldStr + ', "' + itemStr + '")\n'           
    
    # specific field for waveform
    if recordType in {'waveform'}:
        recStr = recStr + '    field(NELM, "' + str(pointNum) + '")\n'
        recStr = recStr + '    field(FTVL, "DOUBLE")\n'

    if recordType in {'waveform-text'}:
        recStr = recStr + '    field(NELM, "' + str(pointNum) + '")\n'
        recStr = recStr + '    field(FTVL, "CHAR")\n'
        
    recStr = recStr + '}\n'
     
    return recStr
    
