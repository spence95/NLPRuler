from rules.Rule import Rule
import nltk
import nltk.data
import re

from nltk import FreqDist
import operator

class FreqDistRule(Rule):
    positivePairs = []
    negativePairs = []
    i = 0

    def __init__(self, name):
        self.name = name

    def prep(self, record, isPositive):
        mostCommonPairs = self.commonOneHundred(record)
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
                            if(testPair[1] > pair[1]):
                                self.positivePairs.insert(index, testPair)
                            index += 1


    def prepStandardPairs(self):
        #positivePairLength = len(self.positivePairs)
        #lengthToRemove = positivePairLength - 100
        #sort positive pairs
        self.positivePairs.sort(key=operator.itemgetter(1), reverse=True)
        #del self.positivePairs[-lengthToRemove:]

    def run(self, record, matchedWordsLimit, matchedScoreLimit):
        mostCommonPairs = self.commonOneHundred(record)

        matchedWords = 0
        matchedScore = 0

        #compare this record's most common pairs with the standard
        for testPair in mostCommonPairs:
            score = 100
            for pair in self.positivePairs:
                if(pair[0] == testPair[0]):
                    #print("Matched: " + pair[0] + " " + testPair[0])
                    matchedWords += 1
                    matchedScore += score
                score -= 1

        if(matchedWords >= matchedWordsLimit and matchedScore >= matchedScoreLimit):
            return True
        else:
            return False

    def commonOneHundred(self, record):
        content = str(record)
        tokens = nltk.word_tokenize(content)
        fdist = FreqDist(tokens)
        return fdist.most_common(100)
