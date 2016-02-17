from __future__ import print_function
import datetime
import os.path
import getpass

import identifyDiagnosisYear
import identifyDrugs
import identifySymptoms
from FinalRecord import FinalRecord
from RecordsManager import RecordsManager


def run():
    ### Run all of our analysis ###
    #get the data we're going to run the analysis on
    username = input("Username to DB? ")
    password = getpass.getpass('Password:')

    rm = RecordsManager("connection", username, password)
    rm.getAllRecords()
    records = rm.records

    #run the diagnosis year analysis (this object pertains to CalledRecordDiagnoseYr class)
    #finalRecords = identifyDiagnosisYear.run(records)

    #run the drugs analysis
    finalRecords = identifyDrugs.run(rm, records)

    #run the symptoms analysis
    #identifySymptoms.run(records, finalRecords)

    ### output all of our info from all the analysis into a tab-delimited text file ###
    diagnosisYrStr = "RUID\tDiagnosis Year\r"
    for record in finalRecords:
        diagnosisYrStr += str(record.ruid) + "\t" + str(record.diagnosisYr) + "\r"

    with open("/home/suttons/MSDataAnalysis/output/diagnosisYears.txt", "a") as txtFile:
        txtFile.write(diagnosisYrStr)

    drugsStr = "RUID\tDrug\tStart Date\tEnd Date\r"
    for record in finalRecords:
        for key in record.drugs:
            drugsStr += str(record.ruid) + "\t" + str(record.drugs[key].name) + "\t" + str(record.drugs[key].startDate) + "\t" + str(record.drugs[key].endDate) + "\r"

    with open("/home/suttons/MSDataAnalysis/output/drugRanges.txt", "a") as txtFile:
        txtFile.write(drugsStr)

run()
