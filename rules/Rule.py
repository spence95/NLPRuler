import nltk
'''
This class is the base class for all rules implemented in the algorithm. All
other rules like ContextRule in diagnosis year rules or ImpressionRule in
diagnosis year rules extend this class and use the main method of run.
'''
class Rule():
    #We use the name attribute when outputting the snippet of text that made the
    #algorithm call it the way it did. We add name so we know what rule made the
    #call
    name = "default"
    def __init__(self, newName):
        self.name = newName

    '''
    This is the main method of the rule class which takes an indefinite amount
    of parameters (usually just the record is enough) and returns either false
    or something else (usually the the Calledrecord object)
    '''
    def run(self, record):
        tokens = nltk.word_tokenize(record)
        text = nltk.Text(tokens)
        coll = text.collocations()
        print(coll)
        return True
