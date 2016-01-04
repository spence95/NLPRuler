from rules.Rule import Rule
import nltk
import nltk.data
import re

class SimpleWordBasedRule(Rule):

    def __init__(self, name):
        self.name = name

    def run(self, record, word):
        tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
        decodedRecord = record.decode("utf-8")
        sentences = tokenizer.tokenize(decodedRecord)
        #tokens = nltk.word_tokenize(record)
        #text = nltk.Text(tokens)
        positiveSentences = []
        for sentence in sentences:
            if re.search(word, sentence):
                positiveSentences.append(sentence)

        if (len(positiveSentences) > 0):
            return True
        else:
            return False
