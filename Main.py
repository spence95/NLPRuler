from __future__ import print_function
from rules.Rule import Rule
from rules.SimpleWordBasedRule import SimpleWordBasedRule
from RecordsManager import RecordsManager
from rules.PhraseListSearchRule import PhraseListSearchRule
from rules.ContextRule import ContextRule
from rules.YearExtractionRule import YearExtractionRule
from rules.FreqDistRule import FreqDistRule
from workers.Worker import Worker
from workers.YearExtractionWorker import YearExtractionWorker

def run():
    foundRecords = 0
    wordBasedRule = SimpleWordBasedRule("SimpleWordBasedRule")
    phraseListSearchRule = PhraseListSearchRule("PhraseListSearchRule")
    contextRule = ContextRule("ContextRule")
    yearExtractionRule = YearExtractionRule("YearExtractionRule")
    freqDistRule = FreqDistRule("FreqDistRule")
    rm = RecordsManager("connection")
    yew = YearExtractionWorker()
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


    rm.getAllRecords()
    records = rm.records

    length = len(records)

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

    runRecordsAnalysis = input("Run records analysis? ")

    if(runRecordsAnalysis == "Y"):
        for record in records:
            i = i + 1
            nextRecordText = record.content
            isPositive = contextRule.run(nextRecordText, phraseList)
            if(isPositive == True):
                #take first four char of record.date for year
                #recordYr = int(record.entry_date[:4])
                recordYr = record.entry_date.year
                recordYr = yew.work(nextRecordText, recordYr)
                masterStr += str(record.ruid) + " " + str(record.entry_date) + " " + str(recordYr) + " " + "\r"
                positives += 1
            else:
                negatives += 1
            progress = round((i/length) * 100, 2)
            print("Progress: " + str(progress) + "%")

        print("Number of positives: " + str(positives))
        print("Number of negatives: " + str(negatives))


    runTrainingSet = input("Run training set? ")

    if(runTrainingSet == "Y"):
        i = 0
        greatestMatched = 0
        masterStr = ""
        yearDiagnoseStr = ""

        trainingSetRecords = rm.getTrainingSetRecords("ValidationSet.txt")
        length = len(trainingSetRecords)

        for record in trainingSetRecords:

            i = i + 1
            nextRecordText = record.content
            #isPositive = wordBasedRule.run(nextRecordText, "has Multiple Sclerosis")
            isPositive = False
            yearCheck = contextRule.run(nextRecordText, phraseList, record.entry_date)
            if(yearCheck != False):
                isPositive = True
                with open("positiveRUIDs.txt", "a") as myfile:
                    string = str(record.ruid) + " ---> " + yearCheck + "\n"
                    myfile.write(string)
                yearDiagnoseStr += str(record.ruid) + " ---> " + str(yearCheck) + "\n"



            if(isPositive):
                if(record.isPositive):
                    if(str(record.diagnosisYr) != str(yearCheck)):
                        falsePositives += 1
                    else:
                        truePositives += 1
                else:
                    #false Positive
                    falsePositives += 1
                    #f = open("falsePositiveText.txt", 'w')
                    #print(nextRecordText, file = f)
            else:
                if(record.isPositive):
                    #false negative
                    falseNegatives += 1
                else:
                    #true negative
                    trueNegatives += 1

            progress = round((i/length) * 100, 2)
            print("Progress: " + str(progress) + "%")



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

    f = open("yearOutput.txt", 'w')
    print(yearDiagnoseStr, file = f)


    #print("Amount of Positive Records " + str(len(positiveRecords)))
    #print("Greatest amount matched: " + str(greatestMatched))

run()
