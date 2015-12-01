from __future__ import print_function
import sys
from rules.Rule import Rule
from rules.SimpleWordBasedRule import SimpleWordBasedRule
from RecordsManager import RecordsManager
from rules.PhraseListSearchRule import PhraseListSearchRule
from rules.ContextRule import ContextRule
from rules.FreqDistRule import FreqDistRule
from workers.Worker import Worker
from workers.YearExtractionWorker import YearExtractionWorker

def run():
    foundRecords = 0
    wordBasedRule = SimpleWordBasedRule("SimpleWordBasedRule")
    phraseListSearchRule = PhraseListSearchRule("PhraseListSearchRule")
    contextRule = ContextRule("ContextRule")
    freqDistRule = FreqDistRule("FreqDistRule")
    rm = RecordsManager("connection")
    yearExtractionWorker = yearExtractionWorker()
    positiveRecords = []

    fileName = "phraseListSymptoms.txt"
    phraseList = []
    category = []
    categories = 0
    with open(fileName) as inputfile:
        for line in inputfile:
            line = line.strip()
            #if line is new category
            if(line[:3] == '+++' and line[-3:] == '+++'):
                categories += 1
                if(categories != 1):
                    phraseList.append(category)
                    category = []
            else:
                category.append(line)

    percentageRequired = .10
    trainingSetRecords = rm.getTrainingSetRecords("TrainingSet.txt")

    validationSetRecords = rm.getTrainingSetRecords("ValidationSet.txt")
    length = len(trainingSetRecords)
    i = 0
    greatestMatched = 0
    masterStr = ""

    trueNegatives = 0
    truePositives = 0
    falseNegatives = 0
    falsePositives = 0

    for record in trainingSetRecords:

        if(record.isPositive):
            freqDistRule.prep(record.content, record.isPositive)

    freqDistRule.prepStandardPairs()

        #By this point we have a standard most common 100 words

    matchedWordsLimit = int(input("Please enter matched words limit: "))
    matchedScoreLimit = int(input("Please enter matched score limit: "))

    masterStr = ""
    for record in validationSetRecords:
        isPositive = freqDistRule.run(record.content, matchedWordsLimit, matchedScoreLimit)

        if(isPositive == True and record.isPositive == True):
            #true positive
            truePositives += 1
            #if isPositive, pull out the diagnosis year
            recordYr = yearExtractionWorker.work(record.content, record.diagnosisYr)
            masterStr += str(record.ruid) + " ---> " + str(recordYr) + "/r"
        if(isPositive == True and record.isPositive == False):
            #false positive
            falsePositives += 1
        if(isPositive == False and record.isPositive == False):
            #true negative
            trueNegatives += 1
        if(isPositive == False and record.isPositive == True):
            #false negative
            falseNegatives += 1



        progress = round((i/length) * 100, 2)
        print("Progress: " + str(progress) + "%")
        i += 1

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

    f = open("yearOutput.txt", 'w')
    print(masterStr, file = f)

run()
