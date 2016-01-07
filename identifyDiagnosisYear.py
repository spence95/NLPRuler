from __future__ import print_function
import datetime
import os.path
import sys

from rules.Rule import Rule
from RecordsManager import RecordsManager
from rules.identifyDiagnosisYearRules.ContextRule import ContextRule
from rules.identifyDiagnosisYearRules.ImpressionRule import ImpressionRule

def run():
    foundRecords = 0
    contextRule = ContextRule("ContextRule")
    impressionRule = ImpressionRule("ImpressionRule")
    rm = RecordsManager("connection")
    positiveRecords = []


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

        #masterDict stores each positive record with that record's corresponding entry date
        #to be ordered later for output (we care about earliest diagnosis and amount of times diagnosed)
        masterDict = {}

        # for record in records:
        #     i = i + 1
        #     if(record.entry_date is not None):
        #         nextRecordText = record.content
        #         isPositive = contextRule.run(nextRecordText, record.entry_date.year)
        #         if(isPositive != False):
        #             #if isPositive isn't False than it's the diagnosis year
        #             diagnosisYr = isPositive
        #             #if ruid not already in masterDict create the list for it
        #             if(record.ruid not in masterDict):
        #                 masterDict[record.ruid] = []
        #             positiveRecordInfo = [record.entry_date, diagnosisYr]
        #             masterDict[record.ruid].append(positiveRecordInfo)
        #             positives += 1
        #         else:
        #             negatives += 1
        #     progress = round((i/length) * 100, 3)
        #     print("Progress: " + str(progress) + "%")
        for record in records:
            i = i + 1
            if(record.entry_date is not None):
                nextRecordText = record.content
                entry_year = int(str(record.entry_date)[:4])
                yearCheck = impressionRule.run(nextRecordText, entry_year)
                if(yearCheck == False):
                    yearCheck = contextRule.run(nextRecordText, entry_year)
                #if yearCheck isn't false than it's a year i.e. 1990
                if(yearCheck != False):
                    #if isPositive isn't False than it's the diagnosis year
                    diagnosisYr = yearCheck
                    #if ruid not already in masterDict create the list for it
                    if(record.ruid not in masterDict):
                        masterDict[record.ruid] = []
                        positiveRecordInfo = [record.entry_date, diagnosisYr]
                        masterDict[record.ruid].append(positiveRecordInfo)
                        positives += 1
                    else:
                        negatives += 1
                    progress = round((i/length) * 100, 3)
                    sys.stdout.write("Script progress: %d%%   \r" % (progress) )
                    sys.stdout.flush()
                    #print("Progress: " + str(progress) + "%")

        print("Number of positives: " + str(positives))
        print("Number of negatives: " + str(negatives))

        for ruid in masterDict:
            #find earliest diagnosis year of the consensus year (the year repeated the most for that patient)
            #find the consensus year
            positiveRecordInfos = masterDict[ruid]
            mostRepeatedDiagnosisYr = 9999
            count = 0
            for positiveRecordInfo in positiveRecordInfos:
                inLoopCount = 0
                for positiveRecordInfoOth in positiveRecordInfos:
                    if(positiveRecordInfo[1] == positiveRecordInfoOth[1]):
                        inLoopCount += 1
                    if(inLoopCount > count):
                        count = inLoopCount
                        mostRepeatedDiagnosisYr = positiveRecordInfo[1]

            #find the earliest date
            index = 0
            for positiveRecordInfo in positiveRecordInfos:
                if(index == 0):
                    earliestEntryDate = datetime.date(9999, 12, 31)
                dateData = str(positiveRecordInfo[0]).split("-")
                recordDate = datetime.date(int(dateData[0]), int(dateData[1]), int(dateData[2]))
                if(recordDate < earliestEntryDate and positiveRecordInfo[1] == mostRepeatedDiagnosisYr):
                    earliestEntryDate = recordDate
                index += 1

            masterStr += "RUID: " + str(ruid) + "\tDiagnosis date: " + str(earliestEntryDate)  + "\tDiagnosis Year: " + str(mostRepeatedDiagnosisYr) + "\tTimes Diagnosis Year Repeated: " + str(count) + "\r"
            for positiveRecordInfo in positiveRecordInfos:
                masterStr += "\t" + str(positiveRecordInfo[0]) + " " + str(positiveRecordInfo[1]) + " " + "\r"






    runTrainingSet = input("Run training set? ")
    falseNegStr = ""
    if(runTrainingSet == "Y"):
        #prelim setup stuff
        i = 0
        greatestMatched = 0
        masterStr = ""
        yearDiagnoseStr = ""
        falsePosStr = ""

        #gets the training set record with positives and negatives taken from Dr. Davis's excel sheet
        trainingSetRecords = rm.getTrainingSetRecords("TotalSet.txt")
        length = len(trainingSetRecords)

        for record in trainingSetRecords:

            i = i + 1
            nextRecordText = record.content
            isPositive = False
            entry_year = int(record.entry_date[:4])
            yearCheck = impressionRule.run(nextRecordText, entry_year)
            if(yearCheck == False):
                yearCheck = contextRule.run(nextRecordText, entry_year)
            #if yearCheck isn't false than it's a year i.e. 1990
            if(yearCheck != False):
                isPositive = True

                with open("/home/suttons/MSDataAnalysis/output/positiveRUIDs.txt", "a") as myfile:
                    string = str(record.ruid) + " ---> " + yearCheck + "\n"
                    myfile.write(string)
                yearDiagnoseStr += str(record.ruid) + " ---> " + str(yearCheck) + "\n"



            if(isPositive):
                if(record.isPositive):
                    if(str(record.diagnosisYr) != str(yearCheck)):
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


    f = open("/home/suttons/MSDataAnalysis/output/output.txt", 'w')
    print(masterStr, file = f)

    f = open("/home/suttons/MSDataAnalysis/output/yearOutput.txt", 'w')
    print(yearDiagnoseStr, file = f)

    f = open("/home/suttons/MSDataAnalysis/output/falseNegOutput.txt", 'w')
    print(falseNegStr, file = f)

    f = open("/home/suttons/MSDataAnalysis/output/falsePosOutput.txt", 'w')
    print(falsePosStr, file = f)



    #print("Amount of Positive Records " + str(len(positiveRecords)))
    #print("Greatest amount matched: " + str(greatestMatched))
