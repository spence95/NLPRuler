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

    trueNegatives = 0
    truePositives = 0
    falseNegatives = 0
    falsePositives = 0

    positives = 0
    negatives = 0
    length = len(records)

    #array to pass to return to the main script to be combined with other NLP scripts
    positiveRecords = {}

    finalRecords = []

    i = 0
    for record in records:
        i = i + 1
        if(record.entry_date is not None):
            entry_year = int(str(record.entry_date)[:4])
            #check becomes False or a year
            #contextrule uses a lot of regex to narrow down the year
            check = contextRule.run(record, entry_year)
            if(check == False):
                #impressionrule exists specifically to call out records where the patient
                #is diagnosed in the visit
                check = impressionRule.run(record, entry_year)

            if(check == False):
                negatives += 1

            #if yearCheck isn't false than it's a year i.e. 1990
            if(check != False):
                positives += 1
                if(check.hardCall):
                    #create final record and append to finalRecords here since hardCall is all like, do it now!
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

    print("Number of positives: " + str(positives))
    print("Number of negatives: " + str(negatives))



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

    #runTrainingSet = input("Run training set? ")
    #training set turned off for now
    runTrainingSet = "N"
    falseNegStr = ""
    if(runTrainingSet == "Y"):
        #prelim setup stuff
        i = 0
        greatestMatched = 0
        yearDiagnoseStr = ""
        falsePosStr = ""

        #gets the training set record with positives and negatives taken from Dr. Davis's excel sheet
        trainingSetRecords = rm.getTrainingSetRecords("TotalSet.txt")
        length = len(trainingSetRecords)

        for record in trainingSetRecords:

            i = i + 1
            isPositive = False
            entry_year = int(record.entry_date[:4])
            check = contextRule.run(record, entry_year)
            if(check == False):
                check = impressionRule.run(record, entry_year)
            #if yearCheck isn't false than it's a year i.e. 1990
            if(check != False):
                isPositive = True

                with open("/home/suttons/MSDataAnalysis/output/positiveRUIDs.txt", "a") as csvFile:
                    regex = re.compile(r'[\n\r\t]')
                    regex.sub(' ', check.calledText)
                    stringLine = str(check.ruid) + "\t" + str(check.entry_date) + "\t" + str(check.calledYear) + "\t" + str(check.calledRule) + "\t" + str(check.calledText) + "\r"
                    csvFile.write(stringLine)
                yearDiagnoseStr += str(record.ruid) + " ---> " + str(check.calledYear) + "\n"



            if(isPositive):
                if(record.isPositive):
                    if(str(record.diagnosisYr) != str(check.calledYear)):
                        falsePositives += 1
                        falsePosStr += str(record.ruid) + " " + str(record.entry_date) + "\r"

                    else:
                        truePositives += 1
                else:
                    #false Positive
                    falsePositives += 1
                    falsePosStr += str(record.ruid) + " " + str(record.entry_date) + " not MS " + "\r"

            else:
                if(record.isPositive):
                    #false negative
                    falseNegatives += 1
                    falseNegStr += str(record.ruid) + " " + str(record.entry_date) + "\r"
                else:
                    #true negative
                    trueNegatives += 1

            progress = round((i/length) * 100, 2)
            sys.stdout.write("Script progress: %d%%   \r" % (progress) )
            sys.stdout.flush()



        print("             ")
        print("             ")
        actualPositives = truePositives + falseNegatives
        actualNegatives = trueNegatives + falsePositives
        #print accuracy: (TP + TN)/total
        accuracy = round(((truePositives + trueNegatives)/length) * 100, 2)
        print("Accuracy (TP + TN)/total: " + str(accuracy) + "%")
        #print misclassification rate: (FP + FN)/total
        misclassificationRate = round(((falsePositives + falseNegatives)/length) * 100, 2)
        print("Misclassification Rate (FP + FN)/total: " + str(misclassificationRate) + "%")
        #print true positive rate: TP/actualPositive
        truePositiveRate = round(((truePositives/actualPositives)) * 100, 2)
        print("True Positive Rate (TP/actual Positives): " + str(truePositiveRate) + "%")
        #print false positive rate: FP/actualNegative
        falsePositiveRate = round(((falsePositives/actualNegatives)) * 100, 2)
        print("False Positive Rate (FP/actual Negatives): " + str(falsePositiveRate) + "%")
        #print specificity: TN/actualNegative
        specificity = round((trueNegatives/actualNegatives) * 100, 2)
        print("Specificity (TN/actual Negatives): " + str(specificity) + "%")
        print("                          ")

        print("True Positives: " + str(truePositives))
        print("True Negatives: " + str(trueNegatives))
        print("False Positives: " + str(falsePositives))
        print("False Negatives: " + str(falseNegatives))




    f = open("/home/suttons/MSDataAnalysis/output/yearOutput.txt", 'w')
    print(yearDiagnoseStr, file = f)

    f = open("/home/suttons/MSDataAnalysis/output/falseNegOutput.txt", 'w')
    print(falseNegStr, file = f)

    f = open("/home/suttons/MSDataAnalysis/output/falsePosOutput.txt", 'w')
    print(falsePosStr, file = f)

    return []
