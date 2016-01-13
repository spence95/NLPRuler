from __future__ import print_function
import datetime
import os.path

import identifyDiagnosisYear
from FinalRecord import FinalRecord


def run():
    ### Run all of our analysis ###

    #run the diagnosis year analysis (this object pertains to CalledRecordDiagnoseYr class)
    finalRecords = identifyDiagnosisYear.run()

    #run the drugs analysis

    #run the symptoms analysis

    ### output all of our info from all the analysis into a tab-delimited text file ###
    finalStr = "RUID\tDiagnosis Year\r"
    for record in finalRecords:
        finalStr += str(record.ruid) + "\t" + str(record.diagnosisYr) + "\r"
    with open("/home/suttons/MSDataAnalysis/output/mainOutput.txt", "a") as txtFile:
        txtFile.write(finalStr)

run()
