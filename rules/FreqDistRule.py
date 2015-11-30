from rules.Rule import Rule
import nltk
import nltk.data
import re

from nltk import FreqDist
import operator

class FreqDistRule(Rule):
    positivePairs = []
    negativePairs = []

    def __init__(self, name):
        self.name = name

    def prep(self, record, isPositive):
        record = str(record)
        tokens = nltk.word_tokenize(record)
        fdist = FreqDist(tokens)
        mostCommonPairs = fdist.most_common(100)
        if(isPositive):
            if(len(self.positivePairs) == 0):
                self.positivePairs = mostCommonPairs
            else:
                isFound = False
                for testPair in mostCommonPairs:
                    index = 0
                    for pair in self.positivePairs:
                        if(pair[0] == testPair[0]):
                            isFound = True
                            newVal = pair[1] + testPair[1]
                            self.positivePairs[index] = (pair[0], newVal)
                        index += 1
                if(isFound == False):
                    for testPair in mostCommonPairs:
                        index = 0
                        for pair in self.positivePairs:
                            print(testPair[1] > pair[1])
                            if(testPair[1] > pair[1]):
                                self.positivePairs.insert(index, testPair)
                                print("inserted")
                            index += 1


    def prepStandardPairs(self):
        #positivePairLength = len(self.positivePairs)
        #lengthToRemove = positivePairLength - 100
        #sort positive pairs
        self.positivePairs.sort(key=operator.itemgetter(1), reverse=True)
        #del self.positivePairs[-lengthToRemove:]




    def run(self):
        print(self.positivePairs)
        print(len(self.positivePairs))
