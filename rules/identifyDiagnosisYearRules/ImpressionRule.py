from rules.Rule import Rule
import nltk
import nltk.data
import re
import difflib

class ImpressionRule(Rule):
    impressionLimit = 250
    diagnosesLimit = 50
    lowerLimit = 100
    upperLimit = 100

    def __init__(self, name):
        self.name = name

    def run(self, record, entry_year):
        msRegex = r'multiple\ssclerosis|multiplesclerosis|\sms\s|:ms\s'
        ### A lot of the positive records I was missing are the ones that are diagnosed in the visit

        #Search for known significant medical diagnoses and conditions and
        #confirm that it isn't MS. Then see if the Impression left afterwards is a diagnosis of MS
        diagnosesRegex = r"medical\sdiagnoses\sand\sconditions.{0," + str(self.diagnosesLimit) + "}|Diagnosis:.{0," + str(self.diagnosesLimit) + "}"
        diagnosesMatch = re.search(diagnosesRegex, record, re.IGNORECASE)
        if(diagnosesMatch):
            msMatch = re.search(msRegex, diagnosesMatch.group(), re.IGNORECASE)
            if(msMatch):
                return False

            impressionRegex = r"Impression:.{0," + str(self.impressionLimit) + "}"
            impressionMatch = re.search(impressionRegex, record, re.IGNORECASE)
            if(impressionMatch):
                msMatch = re.search(msRegex, impressionMatch.group(), re.IGNORECASE)
                if(msMatch):
                        diagnosRegex = r'.{0,' + str(self.lowerLimit) + '}diagnos.{0,' + str(self.upperLimit) + '}'
                        diagnosMatch = re.search(diagnosRegex, impressionMatch.group(), re.IGNORECASE)

                        if(diagnosMatch):
                            return str(entry_year)

        return False
