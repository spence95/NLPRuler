from datetime import date
from collections import OrderedDict
from rules.Rule import Rule
from CalledRecordDiagnoseYr import CalledRecordDiagnoseYr
from operator import itemgetter
import nltk
import nltk.data
import re
import difflib
import sys


class ContextRule(Rule):
    def __init__(self, name):
        self.name = name


    def run(self, record, medName):
        recordContent = record.content
        medNameReal = medName.decode("utf-8").strip()
        medRegex =  r'.{0,100}' + medNameReal + '.{0,100}'
        #instead of 100 characters before and after, we should do
        #two ending chars like ., \n,  \.(.*?)copaxone(.*?)\. 
        medFinds = re.findall(medRegex, recordContent, re.IGNORECASE)
        if(len(medFinds) > 0):
            print(medFinds[0])
            with open("/home/suttons/MSDataAnalysis/output/drugtest.txt", "a") as txtFile:
                stringLine = str(record.ruid) + "\t" + str(record.entry_date) + "\t" + str(medFinds[0]) + "\r"
                txtFile.write(stringLine)
