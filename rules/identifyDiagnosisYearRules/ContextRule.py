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
    upperLimit = 100
    lowerLimit = 100
    yearUpperLimit = 155
    yearLowerLimit = 155
    smallBoundsLimit = 20

    smallerBoundsMSRegex = r'multiple\ssclerosis.{0,' + str(smallBoundsLimit) + '}|' \
    + 'multiplesclerosis.{0,' + str(smallBoundsLimit) + '}|' \
    + '\sMS\s.{0,' + str(smallBoundsLimit) + '}' \
    + '|:MS\s.{0,' + str(smallBoundsLimit) + '}' \
    + '|\sMS-.{0,' + str(smallBoundsLimit) + '}' \
    + '|\sMS\.(?!\s\*\*NAME).{0,' + str(smallBoundsLimit) + '}'

    def __init__(self, name):
        self.name = name

    def run(self, record, entry_year):
        calledRecord = CalledRecordDiagnoseYr(record.ruid, record.entry_date, record.content)
        calledRecord.calledRule = self.name
        record = record.content

        #matches diagnosis, diagnosed, diagnos or multiple sclerosis or ms and returns the upperlimit amount of characters after and the lowerlimit of characters before
        regex = r'.{0,' + str(self.lowerLimit) + '}diagnos.{0,' + str(self.upperLimit) + '}'

        diagnoseMatches = re.findall(regex, record, re.IGNORECASE)
        MSMatches = []

        #get year from entry_date
        yearMaps = []

        for diagnoseMatch in diagnoseMatches:
            #check for negating language here
            #TODO: Use negex package instead of the weak sauce below
            regex = r'\sno.\s|can\'t|cannot|negative|possible'
            negMatches = re.findall(regex, diagnoseMatch, re.IGNORECASE)
            if(len(negMatches) == 0):

                #wording that needs to appear before the ms match
                beforeMSRegex = r'.{0,' + str(self.lowerLimit) + '}multiple\ssclerosis|.{0,' \
                + str(self.lowerLimit) + '}multiplesclerosis|.{0,' \
                + str(self.lowerLimit) + '}\sMS\s' \
                + '|.{0,' + str(self.lowerLimit) + '}:MS\s' \
                + '|.{0,' + str(self.lowerLimit) + '}\sMS\.(?!\s\*\*NAME)'
                beforeMSMatches = re.findall(beforeMSRegex, diagnoseMatch, re.IGNORECASE)
                for beforeMSMatch in beforeMSMatches:
                    #if the specific "diagnosed in" appears before the year than no need for tie breaker, go with that year
                    diagnosedInRegex = "diagnosed\sin\s(19|20)\d{2}"
                    diagnosedInMatch = re.search(diagnosedInRegex, beforeMSMatch, re.IGNORECASE)
                    if(diagnosedInMatch):
                        #this is a hard return
                        calledRecord.calledYear = diagnosedInMatch.group()[-4:]
                        calledRecord.calledText = beforeMSMatch
                        return calledRecord



                #wording that needs to appear after the ms MSMatch
                # afterMSRegex = r'multiple\ssclerosis.{0,' + str(self.upperLimit) + '}|' \
                # + 'multiplesclerosis.{0,' + str(self.upperLimit) + '}|' \
                # + '\sMS\s.{0,' + str(self.upperLimit) + '}' \
                # + '|:MS\s.{0,' + str(self.upperLimit) + '}' \
                # + '|\sMS\.(?!\s\*\*NAME).{0,' + str(self.upperLimit) + '}'
                # afterMSMatches = re.findall(afterMSRegex, diagnoseMatch, re.IGNORECASE)
                # for afterMSMatch in afterMSMatches:

                #special cases of wording
                specialMSRegex = r'(diagnosis\sof\s)((ms|multiplesclerosis|multiple\ssclerosis|))(\swas\smade\sin\s(19|20)\d{2})'
                specialMSMatch = re.search(specialMSRegex, diagnoseMatch, re.IGNORECASE)
                if(specialMSMatch):
                    calledRecord.calledYear = specialMSMatch.group()[-4:]
                    calledRecord.calledText = specialMSMatch.group()
                    return calledRecord

                specialMSRegex = r'diagnosed\swith\s(multiple\ssclerosis|MS|multiplesclerosis)\sin\s(19|20)\d{2}'
                specialMSMatch = re.search(specialMSRegex, diagnoseMatch, re.IGNORECASE)
                if(specialMSMatch):
                    calledRecord.calledYear = specialMSMatch.group()[-4:]
                    calledRecord.calledText = specialMSMatch.group()
                    return calledRecord


                #TODO: Why don't we just search until nearest year?
                #wording that can appear before or after the ms match
                regex = r'.{0,' + str(self.lowerLimit) + '}multiple\ssclerosis.{0,' + str(self.upperLimit) + '}|.{0,' \
                + str(self.lowerLimit) + '}multiplesclerosis.{0,' + str(self.upperLimit) + '}|.{0,' \
                + str(self.lowerLimit) + '}\sMS\s.{0,' + str(self.upperLimit) + '}' \
                + '|.{0,' + str(self.lowerLimit) + '}:MS\s.{0,' + str(self.upperLimit) + '}' \
                + '|.{0,' + str(self.lowerLimit) + '}\sMS\.(?!\s\*\*NAME).{0,' + str(self.upperLimit) + '}'
                MSMatches = re.findall(regex, diagnoseMatch, re.IGNORECASE)
                for MSMatch in MSMatches:
                    #if the phrase "Known Significant Medical Diagnoses and Conditions:" appears in the match
                    #make sure the year is in very close proximity to MS
                    knownDiagnosesRegex = r'known\ssignificant\smedical\sdiagnoses\s'
                    knownDiagnosesMatch = re.search(knownDiagnosesRegex, MSMatch, re.IGNORECASE)
                    if(knownDiagnosesMatch):
                        knownMSMatch = re.search(self.smallerBoundsMSRegex, MSMatch, re.IGNORECASE)
                        if(knownMSMatch):
                            yearRegex = "(19|20)\d{2}"
                            specificYrMatch = re.search(yearRegex, knownMSMatch.group())
                            if(specificYrMatch):
                                specificYr = specificYrMatch.group()
                                calledRecord.calledYear = specificYr
                                calledRecord.calledText = knownMSMatch.group()
                                return calledRecord

                    splitMSMatch = MSMatch.split('.')
                    for splitMatch in splitMSMatch:
                        #search for negating language
                        #look for negating language
                        negRegex = r'\sdoes\snot\s|\scan\'t\s|\swill\snot\s|\scannot\s|\scan\snot\s|\swon\'t\s|\sruledout\s|\sruled\sout\s'
                        negMatch = re.search(negRegex, splitMatch, re.IGNORECASE)

                        if(negMatch):
                            return False

                        diagnosedInRegex = "diagnosed\sin\s(19|20)\d{2}"
                        diagnosedInMatch = re.search(diagnosedInRegex, splitMatch, re.IGNORECASE)
                        if(diagnosedInMatch):
                            #this is a hard return
                            calledRecord.calledYear = diagnosedInMatch.group()[-4:]
                            calledRecord.calledText = splitMatch
                            return calledRecord



                        ### Relative date wording section ###
                        yearsAgoRegex = r"(\d{1,2})\syears\sago"
                        newMatch = re.search(yearsAgoRegex, splitMatch, re.IGNORECASE)
                        if(newMatch):
                            yearsAgo = int(newMatch.group().split(' ')[0])
                            yearsAgoYr = entry_year - yearsAgo
                            calledMap = {'calledYear': yearsAgoYr, 'calledText': MSMatch}
                            yearMaps.append(calledMap)

                        #TODO: last year

                        ### Specific year section ###
                        yearRegex = ".{0,2}(19|20)\d{2}.{0,2}"
                        specificYrMatches = re.finditer(yearRegex, splitMatch, re.IGNORECASE)
                        for specificYrMatch in specificYrMatches:
                            #if DATE[] is in it, ignore it
                            weedOutRegex = "\[|\]|\(|\)"
                            weedOutMatch = re.search(weedOutRegex, specificYrMatch.group(), re.IGNORECASE)
                            if(weedOutMatch):
                                continue

                            #if an s or an ' appears after the number, ignore it because it most likely is
                            #saying early/late in that decade(i.e. 1970s)
                            charAfterYr = specificYrMatch.group()[2:-1][-1:] #gets the letter directly after the year
                            if(charAfterYr == '\'' or charAfterYr == 's'):
                                continue

                            yearRegex = "(19|20)\d{2}"
                            specificYr = re.search(yearRegex, specificYrMatch.group()).group()


                            datesBackRegex = "dat[ie][nsd][g]?\sback\sto"
                            dateMatch = re.search(datesBackRegex, splitMatch, re.IGNORECASE)
                            if(dateMatch):
                                calledMap = {'calledYear': specificYr, 'calledText': MSMatch}
                                yearMaps.append(calledMap)

                            beganRegex = "(symptoms|symptom)\sbegan"
                            beganMatch = re.search(beganRegex, splitMatch, re.IGNORECASE)
                            if(beganMatch):
                                calledMap = {'calledYear': specificYr, 'calledText': MSMatch}
                                yearMaps.append(calledMap)

                            #look for diagnos-ish words but ignore everything after the end of a sentence
                            splitMSMatch = splitMatch.split('.')
                            for splitMatchDiag in splitMSMatch:
                                diagnosRegex = "diagnos."
                                diagnosMatch = re.search(diagnosRegex, splitMatchDiag, re.IGNORECASE)
                                if(diagnosMatch):
                                    yearRegexCheck = re.search(specificYr, splitMatchDiag, re.IGNORECASE)
                                    if(yearRegexCheck):
                                        calledMap = {'calledYear': specificYr, 'calledText': splitMatch}
                                        yearMaps.append(calledMap)



            if(len(yearMaps) > 0):
                #find out the most common year repeated, ties are broken by later year
                yearMaps =  sorted(yearMaps, key=itemgetter('calledYear'), reverse=True)


                commonYr = 0000
                count = 0
                for yearMap in reversed(yearMaps):
                    inLoopCount = 0
                    for yearMapOth in reversed(yearMaps):
                        if(yearMap['calledYear'] == yearMapOth['calledYear']):
                            inLoopCount += 1
                    if(inLoopCount > count):
                        count = inLoopCount
                        commonYr = yearMap['calledYear']


                calledRecord.calledYear = commonYr

                calledText = ""
                #construct all the text used to call this record
                for yearMap in yearMaps:
                    if(yearMap['calledYear'] == commonYr):
                        calledText += yearMap['calledText']
                        calledText += '\t'

                calledRecord.calledText = calledText


                return calledRecord





        return False
