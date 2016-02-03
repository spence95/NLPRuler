from __future__ import print_function
import datetime
import os.path
import sys
import re
import mysql.connector
from mysql.connector import errorcode

from rules.Rule import Rule
from rules.identifyDrugYearRules.ContextRule import ContextRule


#def run(records, finalRecords):
def run(finalRecords, rm):
    records = []
    #TODO: ruids are hardcoded for now, need to get them from finalRecords instead
    ruids = [
    7,
    10,
    67,
    68,
    69,
    71,
    72,
    74,
    75,
    79,
    80,
    101,
    109,
    119,
    194,
    195,
    196,
    197,
    199,
    200,
    201,
    202,
    203,
    205,
    210,
    212,
    213
    ]

    #TODO: read in all symptoms from symptoms.txt isntead of hardcoding like below
    #TODO: also would have to treat each line in txt file, replacing ' ' with \s
    symptoms = {
    'Injection Site Problems' : [
        'necrosis',
        'blisters',
        'Stevens-Johnson\ssyndrome',
        'toxic\sepidermal\snecrolysis'
        'skin\sinfections',
        'cellulitis',
        'angioedema',
        'hematoma',
        'erythema',
        'erythematous\srash',
        'maculopapular\srash',
        'abscess',
        'blue\sdiscoloration',
        'black\sdiscoloration',
        'lipoatrophy',
        'benign\sneoplasm',
        'injection\ssite\sfibrosis'
        ]
    }

    for ruid in ruids:
        for record in rm.getRecordsForRuid('where ruid = ' + str(ruid)):
            records.append(record)

    length = len(records)
    i = 0

    for record in records:
        for key in symptoms:
            for symptom in symptoms[key]:
                #search record for any of the above symptoms
                #symptomRegex =  r'\.(.*?)' + symptom + '(.*?)\.'
                symptomRegex = r'.{0,50}' + symptom + '.{0,50}'
                find = re.search(symptomRegex, record.content)
                if(find):
                    print(find.group())
        progress = round((i/length) * 100, 2)
        sys.stdout.write("Identifying symptoms... %d%%   \r" % (progress) )
        sys.stdout.flush()
        i += 1
