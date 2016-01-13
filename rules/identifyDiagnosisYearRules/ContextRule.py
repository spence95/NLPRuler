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



                #wording that can appear before or after the ms match
                regex = r'.{0,' + str(self.lowerLimit) + '}multiple\ssclerosis.{0,' + str(self.upperLimit) + '}|.{0,' \
                + str(self.lowerLimit) + '}multiplesclerosis.{0,' + str(self.upperLimit) + '}|.{0,' \
                + str(self.lowerLimit) + '}\sMS\s.{0,' + str(self.upperLimit) + '}' \
                + '|.{0,' + str(self.lowerLimit) + '}:MS\s.{0,' + str(self.upperLimit) + '}' \
                + '|.{0,' + str(self.lowerLimit) + '}\sMS\.(?!\s\*\*NAME).{0,' + str(self.upperLimit) + '}'
                MSMatches = re.findall(regex, diagnoseMatch, re.IGNORECASE)
                for MSMatch in MSMatches:

                    ### Relative date wording section ###
                    yearsAgoRegex = "/(\d{1,2})\s+years\s+ago/"
                    newMatch = re.search(yearsAgoRegex, MSMatch, re.IGNORECASE)
                    if(newMatch):
                        yearsAgo = int(newMatch.split(' ')[0])
                        yearsAgoYr = entry_year - yearsAgo
                        calledMap = {'calledYear': yearsAgoYr, 'calledText': MSMatch}
                        yearMaps.append(calledMap)

                    #TODO: last year

                    ### Specific year section ###
                    yearRegex = ".{0,2}(19|20)\d{2}.{0,2}"
                    specificYrMatches = re.finditer(yearRegex, MSMatch, re.IGNORECASE)
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

                        #take first two and last two chars off of year match
                        specificYr = specificYrMatch.group()[2:-2]

                        datesBackRegex = "dat[ie][nsd][g]?\sback\sto"
                        dateMatch = re.search(datesBackRegex, MSMatch, re.IGNORECASE)
                        if(dateMatch):
                            calledMap = {'calledYear': specificYr, 'calledText': MSMatch}
                            yearMaps.append(calledMap)

                        beganRegex = "(symptoms|symptom)\sbegan"
                        beganMatch = re.search(beganRegex, MSMatch, re.IGNORECASE)
                        if(beganMatch):
                            calledMap = {'calledYear': specificYr, 'calledText': MSMatch}
                            yearMaps.append(calledMap)

                        #look for diagnos-ish words but ignore everything after the end of a sentence
                        splitMSMatch = MSMatch.split('.')
                        for splitMatch in splitMSMatch:
                            diagnosRegex = "diagnos."
                            diagnosMatch = re.search(diagnosRegex, splitMatch, re.IGNORECASE)
                            if(diagnosMatch):
                                yearRegexCheck = re.search(specificYr, splitMatch, re.IGNORECASE)
                                if(yearRegexCheck):
                                    calledMap = {'calledYear': specificYr, 'calledText': MSMatch}
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
