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
    finalRecords = identifyDiagnosisYear.run(records)

    #run the drugs analysis
    finalRecords = identifyDrugs.run(rm, records, finalRecords)

    #run the symptoms analysis
    #identifySymptoms.run(finalRecords, rm)

    ### output all of our info from all the analysis into a tab-delimited text file ###
    finalStr = "RUID\tDiagnosis Year\r"
    for record in finalRecords:
        finalStr += str(record.ruid) + "\t" + str(record.diagnosisYr) + "\r"
        finalStr += "Drugs\tDrug Dates\tSymptoms\tSymptom Dates\r"
        for drug in record.drugs:
            for date in record.drugs[drug]:
                finalStr += str(drug) + "\t" + str(date) + "\r"
    with open("/home/suttons/MSDataAnalysis/output/mainOutput.txt", "a") as txtFile:
        txtFile.write(finalStr)

run()
