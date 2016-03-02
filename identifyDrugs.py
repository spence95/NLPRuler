from __future__ import print_function
import datetime
import os.path
import sys
import re
import mysql.connector
from mysql.connector import errorcode

from rules.Rule import Rule
from rules.identifyDrugYearRules.ContextRule import ContextRule
from FinalRecord import FinalRecord



#def run(records, finalRecords):
#def run(rm, records, finalRecords):
def run(rm, records):
    totalMeds = {}
    ruids = []

        #get a list of drugs per patient ruid
    # for finalRecord in finalRecords:
    #     if finalRecord.ruid not in ruids:
    #         ruids.append(finalRecord.ruid)





    #use a mocked out set of positives to speed testing up
    ruids = [
    7	,
    10	,
    67	,
    68	,
    69	,
    71	,
    72	,
    74	,
    75	,
    79	,
    80	,
    101	,
    109	,
    119	,
    194	,
    195	,
    196	,
    197	,
    199	,
    200	,
    201	,
    202	,
    203	,
    205	,
    210	,
    212	,
    213	,
    231	,
    278	,
    362	,
    373	,
    376	,
    383	,
    387	,
    404	,
    407	,
    554	,
    555	,
    556	,
    560	,
    561	,
    562	,
    564	,
    567	,
    597	,
    625	,
    626	,
    627	,
    629	,
    631	,
    633	,
    637	,
    639	,
    640	,
    641	,
    653	,
    671	,
    674	,
    711	,
    715	,
    719	,
    720	,
    724	,
    741	,
    760	,
    762	,
    764	,
    850	,
    851	,
    854
    ]

    finalRecords = []

    for ruid in ruids:
        fr = FinalRecord()
        fr.ruid = ruid
        finalRecords.append(fr)


    contextRule = ContextRule("ContextRule", finalRecords)




    #take each patient found in identify diagnosis year, check all their records to find the drugs
    i = 0
    length = len(records)
    for record in records:
        if(record.ruid in ruids):
            check = contextRule.run(record)
        i += 1
        progress = round((i/length) * 100, 2)
        sys.stdout.write("Identifying drug dates... %d%%   \r" % (progress) )
        sys.stdout.flush()

    return contextRule.finalRecords

    # for ruid in contextRule.masterDict:
    #     with open("/home/suttons/MSDataAnalysis/output/drugtest.txt", "a") as txtFile:
    #         stringLine = "RUID: " + str(ruid) + "\r"
    #         txtFile.write(stringLine)
    #     for drug in contextRule.masterDict[ruid]:
    #         with open("/home/suttons/MSDataAnalysis/output/drugtest.txt", "a") as txtFile:
    #             stringLine = "\t" + str(drug) + "\r"
    #             txtFile.write(stringLine)
    #         for date in contextRule.masterDict[ruid][drug]:
    #             with open("/home/suttons/MSDataAnalysis/output/drugtest.txt", "a") as txtFile:
    #                 stringLine = "\t\t" + str(date) + "\r"
    #                 txtFile.write(stringLine)
