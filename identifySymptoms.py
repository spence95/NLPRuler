from __future__ import print_function
import datetime
import os.path
import sys
import re
import mysql.connector
from mysql.connector import errorcode
from nltk import tokenize

from rules.Rule import Rule
from rules.identifyDrugYearRules.ContextRule import ContextRule


def run(records, finalRecords):
    records = []
    
    #TODO: read in all symptoms from symptoms.txt isntead of hardcoding like below
    #TODO: also would have to treat each line in txt file, replacing ' ' with \s
    symptoms = [
    'Fatigue'
    'Gait'
    'Numbness',
    'Tingling',
    'Spasticity',
    'Weakness',
    'Blurred\sVision',
    'Vision\sProblems',
    'Dizziness',
     'Vertigo'
     ]

     ruids = []
     #get a list of drugs per patient ruid
     for finalRecord in finalRecords:
         if finalRecord.ruid not in ruids:
             ruids.append(finalRecord.ruid)

     length = len(records)
     i = 0

     for record in records:
         if record.ruid in ruids:
             sentences = tokenize.sent_tokenize(record.content)
             for sentence in sentences:
                 for symptom in symptoms:
                     #search record for any of the above symptoms
                     #symptomRegex =  r'\.(.*?)' + symptom + '(.*?)\.'
                     #symptomRegex = r'.{0,50}' + symptom + '.{0,50}'
                     find = re.search(symptom, sentence, re.IGNORECASE)
                     if(find):
                         negRegex = "cannot|can\'t|not\sable|won\'t"
                         neg = re.search(neg, sentence)
                         if(neg is None):
                             for fr in finalRecords:
                                 if fr.ruid == record.ruid:
                                     #add symptom and entry date to final record symptom dict
                                     if symptom not in fr.symptoms:
                                         fr.drugs[symptom] = [record.entry_date]
                                     else:
                                         fr.drugs[symptom].append(record.entry_date)
         progress = round((i/length) * 100, 2)
         sys.stdout.write("Identifying symptoms... %d%%   \r" % (progress) )
         sys.stdout.flush()
         i += 1
