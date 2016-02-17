from datetime import date
from collections import OrderedDict
from rules.Rule import Rule
from CalledRecordDiagnoseYr import CalledRecordDiagnoseYr
from drug import Drug
from operator import itemgetter
import nltk
import nltk.data
import re
import difflib
import sys


class ContextRule(Rule):
    drugNames = []
    masterDict = {}
    finalRecords = []
    def __init__(self, name, finalRecords):
        self.name = name
        self.drugNames = self.getDrugNames()
        self.finalRecords = finalRecords



    def run(self, record):
        if(record.ruid not in self.masterDict):
            self.masterDict[record.ruid] = {}
        #TODO: the medications part of this regex needs to get until the end of listed medications, not just 1000 characters after
        prescriptionsRegex = r'Medications\sKnown\sto\sbe\sPrescribed(.*?)--|Medications:.{0,1000}'
        prescriptionsSearch = re.search(prescriptionsRegex, record.content, re.IGNORECASE)
        if(prescriptionsSearch):
            for drugName in self.drugNames:
                drugNameSearch = re.search(drugName, prescriptionsSearch.group(), re.IGNORECASE)
                if(drugNameSearch):
                    #find the final records with the corresponding ruid
                    for fr in self.finalRecords:
                        if fr.ruid == record.ruid:
                            #add drug and entry date to final record drug dict
                            if drugName not in fr.drugs:
                                dr = Drug()
                                dr.name = drugName
                                dr.startDate = record.entry_date
                                dr.endDate = record.entry_date
                                fr.drugs[drugName] = dr
                            else:
                                #get start date for that drug and see if this date is before it
                                if record.entry_date < fr.drugs[drugName].startDate:
                                    fr.drugs[drugName].startDate = record.entry_date
                                #get end date for that drug and see if this date is after it
                                elif record.entry_date > fr.drugs[drugName].endDate:
                                    fr.drugs[drugName].endDate = record.entry_date


    def splitUpSearch(self, text):
        hyphenCount = text.count('-')
        commaCount = text.count(',')
        # periodCount = text.count('.')
        lowerUpperCount = 0
        lastLetterLower = False
        for letter in text:
            if(letter.isupper() == False and letter != ' '):
                lastLetterLower = True
            elif(letter.isupper() == True and lastLetterLower == True):
                lowerUpperCount += 1
                lastLetterLower = False
            else:
                lastLetterLower = False
        countList = [hyphenCount, commaCount, lowerUpperCount]
        maxCount = max(countList)
        if(maxCount > 0):
            i = 0
            for count in countList:
                if(count == maxCount):
                    if i == 0:
                        return '-'
                    elif i == 1:
                        return ','
                    # elif i == 2:
                    #     return '.'
                    elif i == 2:
                        return 'upper'
                i += 1
        return False


    def pickOutTags(self, tagged, drug, medName):
        #get from end of medicine name to next proper noun
        for tag in tagged:
            if tag[0] not in str(medName):
                if tag[1] == 'NNP' and tag[0] != 'Medications':
                    break
                #cardinal number -> dosage
                if tag[1] == 'CD':
                    drug.dosage = tag[0]

                #adjectives -> how often
                if(tag[1] == 'JJ'):
                    drug.freq = tag[0]

                #adverb -> check if 'once' then it's how often
                if(tag[1] == 'RB'):
                    drug.freq = tag[0] + drug.freq

                #noun -> usually how i.e. capsules, injection
                if((tag[1] == 'NN' or tag[1] == 'NNS') and tag[0] != 'Medications'):
                    drug.manner = tag[0]
        return drug


    def spaceBeforeCapilizedWords(self, sentence):
        i = 0
        for letter in sentence:
            if i > 0:
                if letter.isupper():
                    if(sentence[i - 1] != ' '):
                        sentence = sentence[:i] + ' ' + sentence[i:]
                        i += 1
            i += 1

        return sentence


    def getDrugNames(self):
        drugNames = [
        'Avonex',
        'Betaseron',
        'Copaxone',
        'Extavia',
        'Glatopa',
        'Plegridy',
        'Rebif',
        'Aubagio',
        'Gilenya',
        'Tecfidera',
        'Lemtrada',
        'Novantrone',
        'Tysabri'
        ]
        return drugNames
