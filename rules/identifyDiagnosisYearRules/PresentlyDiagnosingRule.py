from rules.Rule import Rule
from CalledRecordDiagnoseYr import CalledRecordDiagnoseYr
import nltk
import nltk.data
import re

class PresentlyDiagnosingRule(Rule):
    impressionLimit = 250
    diagnosesLimit = 125
    lowerLimit = 120
    upperLimit = 120
    msLimit = 25

    def __init__(self, name):
        self.name = name

    def run(self, record, entry_year):
        calledRecord = CalledRecordDiagnoseYr(record.ruid, record.entry_date, record.content)
        calledRecord.calledRule = self.name
        record = record.content

        #findings are consistent with multiple sclerosis
        #in all likelihood, he has primary progressive multiple sclerosis
        #confident that he/she has multiple sclerosis
