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

def run():
    foundRecords = 0
    contextRule = ContextRule("ContextRule")
    impressionRule = ImpressionRule("ImpressionRule")
    rm = RecordsManager("connection")


    percentageRequired = .10

    i = 0
    greatestMatched = 0
    masterStr = ""
    yearDiagnoseStr = ""

    trueNegatives = 0
    truePositives = 0
    falseNegatives = 0
    falsePositives = 0

    positives = 0
    negatives = 0

    #This is running the analysis against records of unknown diagnosis, it's testing the algorithm out for real
    runRecordsAnalysis = input("Run records analysis? ")

    if(runRecordsAnalysis == "Y"):
        rm.getAllRecords()
        records = rm.records
        length = len(records)


        #array to pass to return to the main script to be combined with other NLP scripts
        positiveRecords = {}

        for record in records:
            i = i + 1
            if(record.entry_date is not None):
                entry_year = int(str(record.entry_date)[:4])
                check = contextRule.run(record, entry_year)
                if(check == False):
                    check = impressionRule.run(record, entry_year)

                if(check == False):
                    negatives += 1

                    #if yearCheck isn't false than it's a year i.e. 1990
                if(check != False):
                    positives += 1
                    if(check.ruid not in positiveRecords):
                        positiveRecords[check.ruid] = [check]
                    else:
                        positiveRecords[check.ruid].append(check)
                    with open("/home/suttons/MSDataAnalysis/output/positiveRUIDsFullRecords.txt", "a") as txtFile:
                        regex = re.compile(r'[\n\r\t]')
                        regex.sub(' ', check.calledText)
                        stringLine = str(check.ruid) + "\t" + str(check.entry_date) + "\t" + str(check.calledYear) + "\t" + str(check.calledRule) + "\t" + str(check.calledText) + "\r"
                        txtFile.write(stringLine)
            progress = round((i/length) * 100, 2)
            sys.stdout.write("Script progress: %d%%   \r" % (progress) )
            sys.stdout.flush()

        print("Number of positives: " + str(positives))
        print("Number of negatives: " + str(negatives))



    #find the most frequent year and return that with the ruid
    finalRecords = []
    for key in positiveRecords:
        positiveRecordsForRuid = positiveRecords[key]
        commonYr = 0
        count = 0
        finalRecord = FinalRecord()
        finalRecord.ruid = positiveRecordsForRuid[0].ruid
        for record in positiveRecordsForRuid:
            prevCount = count
            for othRecord in positiveRecordsForRuid:
                if(record.calledYear == othRecord.calledYear):
                    count += 1
            if(count > prevCount):
                commonYr = record.calledYear
        finalRecord.diagnosisYr = commonYr
        finalRecords.append(finalRecord)

    print("Done!")


    return finalRecords










    runTrainingSet = input("Run training set? ")
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



    #print("Amount of Positive Records " + str(len(positiveRecords)))
    #print("Greatest amount matched: " + str(greatestMatched))
