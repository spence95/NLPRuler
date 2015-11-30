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
            freqDistRule.prep(record, isPositive)



        '''
        i = i + 1
        nextRecordText = record.content
        #isPositive = wordBasedRule.run(nextRecordText, "has Multiple Sclerosis")

        isPositive = contextRule.run(nextRecordText, phraseList)
        if(isPositive):
        '''
            '''
            matched = phraseListSearchRule.run(nextRecordText, phraseList, percentageRequired)
            if((matched/categories) < percentageRequired):
                isPositive = False
                if(record.isPositive):
                    #false negative
                    falseNegatives += 1
                else:
                    #true negative
                    trueNegatives += 1
            else:
                positiveRecords.append(record)
                masterStr += str(record.ruid) + " " + str(record.entry_date) + " " + str(isPositive) + "\n"
            '''
            '''
            positiveRecords.append(record)
            masterStr += str(record.ruid) + " " + str(record.entry_date) + " " + str(isPositive) + "\n"
            #check for data science statistic
            if(record.isPositive):
                #true Positive
                truePositives += 1
            else:
                #false Positive
                falsePositives += 1
                f = open("falsePositiveText.txt", 'w')
                print(nextRecordText, file = f)
        else:
            if(record.isPositive):
                #false negative
                falseNegatives += 1
            else:
                #true negative
                trueNegatives += 1
            '''

        progress = round((i/length) * 100, 2)
        print("Progress: " + str(progress) + "%")

    freqDistRule.prepStandardPairs()
    freqDistRule.run()


    '''
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


    f = open("output.txt", 'w')
    print(masterStr, file = f)
    '''


    #print("Amount of Positive Records " + str(len(positiveRecords)))
    #print("Greatest amount matched: " + str(greatestMatched))

run()
