from rules.Rule import Rule
import nltk
import nltk.data
import re

class PhraseListWeightedSearchRule(Rule):
    def __init__(self, name):
        self.name = name
