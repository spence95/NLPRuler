from rules.Rule import Rule
from CalledRecordDiagnoseYr import CalledRecordDiagnoseYr
import nltk
import nltk.data
import re
import difflib

class ImpressionRule(Rule):
    impressionLimit = 250
    diagnosesLimit = 50
    lowerLimit = 120
    upperLimit = 120
    msLimit = 25

    years = []

    def __init__(self, name):
        self.name = name

    def run(self, record, entry_year):
        calledRecord = CalledRecordDiagnoseYr(record.ruid, record.entry_date, record.content)
        calledRecord.calledRule = self.name
        record = record.content
        msRegex = r'.{0, ' + str(self.msLimit) + 'multiple\ssclerosis|multiplesclerosis|\sms\s|:ms\s.{0,' + str(self.msLimit) + '}'
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
                        #look for negating language
                        # negRegex = r'not|can\'t|will\snot|cannot|can\snot|won\'t|ruledout|ruled\sout'
                        # negMatch = re.search(negRegex, msMatch.group(), re.IGNORECASE)
                        #
                        # if(negMatch):
                        #     return False

                        #at this point, the patient has MS, this only picks out the ones being presently diagnosed
                        diagnosRegex = r'.{0,' + str(self.lowerLimit) + '}diagnos.{0,' + str(self.upperLimit) + '}'
                        diagnosMatch = re.search(diagnosRegex, msMatch.group(), re.IGNORECASE)

                        if(diagnosMatch):
                            calledRecord.calledYear = str(entry_year)
                            calledRecord.calledText = msMatch.group() + '\t' + diagnosMatch.group()
                            return calledRecord

        return False
