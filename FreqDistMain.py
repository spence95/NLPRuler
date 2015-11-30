from __future__ import print_function
from rules.Rule import Rule
from rules.SimpleWordBasedRule import SimpleWordBasedRule
from RecordsManager import RecordsManager
from rules.PhraseListSearchRule import PhraseListSearchRule
from rules.ContextRule import ContextRule
from rules.FreqDistRule import FreqDistRule

def run():
    foundRecords = 0
    wordBasedRule = SimpleWordBasedRule("SimpleWordBasedRule")
    phraseListSearchRule = PhraseListSearchRule("PhraseListSearchRule")
    contextRule = ContextRule("ContextRule")
    freqDistRule = FreqDistRule("FreqDistRule")
    rm = RecordsManager("connection")
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



        progress = round((i/length) * 100, 2)
        print("Progress: " + str(progress) + "%")
        i += 1

    freqDistRule.prepStandardPairs()
    freqDistRule.run()





    #print("Amount of Positive Records " + str(len(positiveRecords)))
    #print("Greatest amount matched: " + str(greatestMatched))

run()
