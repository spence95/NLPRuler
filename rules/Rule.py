import nltk
class Rule():
    name = "default"
    def __init__(self, newName):
        self.name = newName

    def run(self, record):
        tokens = nltk.word_tokenize(record)
        text = nltk.Text(tokens)
        coll = text.collocations()
        print(coll)
        return True
