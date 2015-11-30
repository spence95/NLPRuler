from rules.Rule import Rule
import nltk
import nltk.data
import re

class PhraseListSearchRule(Rule):
    def __init__(self, name):
        self.name = name

    def run(self, record, phraseList, percentageTrue):
        matched = 0
        listLen = len(phraseList)
        #decodedRecord = record.decode("utf-8")
        for category in phraseList:
            for item in category:
                if re.search(item, record, re.IGNORECASE):
                #if re.search(item, record):
                    #grab the sentence or context that it's in
                    #tokenize that sentence
                    #decide if that sentence is negating the match or confirming it i.e. "the patient does not have ..."
                    print("matched")
                    matched += 1
                    break

        return matched
