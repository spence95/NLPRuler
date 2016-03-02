from __future__ import print_function
import datetime
import os.path
import sys
import re

from rules.Rule import Rule
from CalledRecordDiagnoseYr import CalledRecordDiagnoseYr
from RecordsManager import RecordsManager
from rules.identifyDiagnosisYearRules.ContextRule import ContextRule
from rules.identifyDiagnosisYearRules.ImpressionRule import ImpressionRule
from FinalRecord import FinalRecord

def run(records):
    #setup info
    contextRule = ContextRule("ContextRule")
    impressionRule = ImpressionRule("ImpressionRule")

    #length is used to show progress of script to user
    length = len(records)

    #array to pass to return to the main script to be combined with other NLP scripts
    positiveRecords = {}

    #what eventually is returned. Composed of finalRecord objects
    finalRecords = []

    i = 0
    #records was retrieved from RecordsManager.py in Main.py then passed to this script
    for record in records:
        i = i + 1
        #sometimes the record doesn't even have an entry_date, we can't use that
        if(record.entry_date is not None):
            #Get the last four digits of entry_date which is the year
            entry_year = int(str(record.entry_date)[:4])
            #check becomes False or a called record object
            #contextrule uses a lot of regex to narrow down the year
            check = contextRule.run(record, entry_year)
            if(check == False):
                #impressionrule exists specifically to call out records where the patient
                #is diagnosed in the visit
                check = impressionRule.run(record, entry_year)

            #if yearCheck isn't false than it's a year i.e. 1990
            if(check != False):
                if(check.hardCall):
                    #create final record and append to finalRecords here since hardCall
                    #means that we are sure that it's this last diagnosis year we saw
                    finalRecord = FinalRecord()
                    finalRecord.ruid = record.ruid
                    #make sure it isn't already there
                    notInFinalRecords = True
                    for record in finalRecords:
                        if(record.ruid == finalRecord.ruid):
                            notInFinalRecords = False
                    if(notInFinalRecords):
                        finalRecord.diagnosisYr = check.calledYear
                        finalRecords.append(finalRecord)
                else:
                    #if ruid already seen, pair it with previous info
                    if(check.ruid not in positiveRecords):
                        positiveRecords[check.ruid] = [check]
                    else:
                        positiveRecords[check.ruid].append(check)

                #a file to help understand what's happening during the analysis
                with open("/home/suttons/MSDataAnalysis/output/positiveRUIDsFullRecordsDiagnoseYr.txt", "a") as txtFile:
                    regex = re.compile(r'[\n\r\t]')
                    regex.sub(' ', check.calledText)
                    stringLine = str(check.ruid) + "\t" + str(check.entry_date) + "\t" + str(check.calledYear) + "\t" + str(check.calledRule) + "\t" + str(check.calledText) + "\r"
                    txtFile.write(stringLine)

        #show the progress of the script
        progress = round((i/length) * 100, 2)
        sys.stdout.write("Identifying diagnosis years... %d%%   \r" % (progress) )
        sys.stdout.flush()


    #find the most frequent year and return that with the ruid
    for key in positiveRecords:
        #used to throw out records that have multiple different diagnosis dates
        countList = []
        positiveRecordsForRuid = positiveRecords[key]
        commonYr = 0
        count = 0
        finalRecord = FinalRecord()
        finalRecord.ruid = positiveRecordsForRuid[0].ruid


        years = []
        for record in positiveRecordsForRuid:

            #build a list of years for this record i.e. [1976, 1976] or [1992, 1992, 1995, 1995]
            years.append(record.calledYear)

        #order the list
        years = sorted(years, key=int, reverse=True)
        #count first item, check if next item is same, if it is incremnt count, if not add count to countList and add one to count
        countList = []
        #make a distinct set of years
        distinctYears = list(set(years))
        distinctYears = sorted(distinctYears, key=int, reverse=True)
        #remove years that are close together from distinct list
        index = 0
        for distYear in distinctYears:
            for distYearOth in distinctYears:
                if(distYear != distYearOth):
                    if(abs(int(distYear) - int(distYearOth)) <= 3):
                        del distinctYears[index]
            index += 1

        #make a list of counting, if the lowest element in count list is lower than all other elements, we good
        highestCount = 0
        commonYr = 0
        for distYear in distinctYears:
            count = 0
            for year in years:
                if(abs(int(year) - int(distYear)) <= 3):
                    count += 1
            if(count > highestCount):
                highestCount = count
                commonYr = distYear
            countList.append(count)

        #TODO: If the algorithm only identifies one diagnosis date not from a hard rule, throw it out


        #check the length countlist i.e. [2] or [2, 2]
        #if the length is one, we're good
        if(len(countList) == 1):
            #make sure ruid isn't already in finalRecords
            notInFinalRecords = True
            for record in finalRecords:
                if(record.ruid == finalRecord.ruid):
                    notInFinalRecords = False
            if(notInFinalRecords):
                finalRecord.diagnosisYr = commonYr
                finalRecords.append(finalRecord)
        else:
            #order the countlist
            countList = sorted(countList, key=int, reverse=True)
            #if the first item is greater than the second item we're good
            if(countList[0] > countList[1]):
                #make sure ruid isn't already in finalRecords
                notInFinalRecords = True
                for record in finalRecords:
                    if(record.ruid == finalRecord.ruid):
                        notInFinalRecords = False
                if(notInFinalRecords):
                    finalRecord.diagnosisYr = commonYr
                    finalRecords.append(finalRecord)


    print("Done with Diagnosis years!")
    return finalRecords
