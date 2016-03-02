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
    #these limits are used in regex to get surrounding context
    upperLimit = 100
    lowerLimit = 100
    yearUpperLimit = 155
    yearLowerLimit = 155
    #below is used in regex for header information
    smallBoundsLimit = 20

    #this is a bit of regex used repeatedly throughout  this script, explanation for
    #why I did it this way can be found in other parts
    #the last one gets MS. when it isn't a title for a person
    smallerBoundsMSRegex = r'multiple\ssclerosis.{0,' + str(smallBoundsLimit) + '}|' \
    + 'multiplesclerosis.{0,' + str(smallBoundsLimit) + '}|' \
    + '\sMS\s.{0,' + str(smallBoundsLimit) + '}' \
    + '|:MS\s.{0,' + str(smallBoundsLimit) + '}' \
    + '|\sMS-.{0,' + str(smallBoundsLimit) + '}' \
    + '|\sMS\.(?!\s*\*\*NAME).{0,' + str(smallBoundsLimit) + '}' \
    + '|:MS-.{0,' + str(smallBoundsLimit) + '}'

    #the name attribute is only important for knowing what rule called the diagnosis year
    #which for this part it would only either be the context rule or the impression rule
    #and most of the time it's the context rule
    def __init__(self, name):
        self.name = name

    def run(self, record, entry_year):
        #some general organizing stuff for later when it comes to outputting record data
        calledRecord = CalledRecordDiagnoseYr(record.ruid, record.entry_date, record.content)
        #lets me know as I check the accuracy of the algorithm that it was this rule that called the year
        calledRecord.calledRule = self.name

        #matches diagnosis, diagnosed, diagnos or multiple sclerosis or ms and returns the upperlimit amount of characters after and the lowerlimit of characters before
        #I use this kind of regex a lot -> .{0, (some number)}(other regex).{0, (some number)} and all it does is grabs the amount of characters in that direction so
        # .{0,100}diagnos.{0,100} would grab 100 characters before and after any 'diagnos' string
        regex = r'.{0,' + str(self.lowerLimit) + '}diagnos.{0,' + str(self.upperLimit) + '}'
        #re.IGNORECASE is really important. It slows down the algorithm A LOT but it greatly increases its accuracy
        diagnoseMatches = re.findall(regex, record.content, re.IGNORECASE)

        #used to find out the most common year repeated in this one record
        yearMaps = []

        for diagnoseMatch in diagnoseMatches:
            #even though it's only around 200 characters total, I found
            #that splitting it up by sentence was still helpful to rule out
            #false positives. We also split it up by new line, >, <, in addition
            #to periods.
            #splitDiagnoseMatches = diagnoseMatch.split('.')
            #I took this sentence split from Dr. Davis's script here remarks are:
            ####Split the note into sentences or phrases. ---- and >< were common things I found that displayed long lists
            ####instead of phrases and made my searching more difficult
            splitDiagnoseMatches = diagnoseMatch.split('(?:\.\s+)|(?:-(?:\s+)?)+|(?:>\s?<)|\\n')
            #for each sentence
            for splitDiagnoseMatch in splitDiagnoseMatches:
                #Check for negating language here. This could be done better but serves our
                #purposes for now
                regex = r'\sno.\s|can\'t|cannot|negative|possible'
                negMatches = re.findall(regex, splitDiagnoseMatch, re.IGNORECASE)

                #if there aren't any negative language
                if(len(negMatches) == 0):
                    #Checks for wording that needs to appear before any variation of MS
                    #the amount of characters to check preceding MS is degined by lowerlimit at the
                    #start of this record
                    beforeMSRegex = r'.{0,' + str(self.lowerLimit) + '}multiple\ssclerosis|.{0,' \
                    + str(self.lowerLimit) + '}multiplesclerosis|.{0,' \
                    + str(self.lowerLimit) + '}\sMS\s' \
                    + '|.{0,' + str(self.lowerLimit) + '}:MS\s' \
                    + '|.{0,' + str(self.lowerLimit) + '}\sMS\.(?!\s*\*\*NAME)' \
                    + '|.{0,' + str(self.lowerLimit) + '}:MS-.'
                    beforeMSMatches = re.findall(beforeMSRegex, splitDiagnoseMatch, re.IGNORECASE)
                    #iterate through all the matches
                    for beforeMSMatch in beforeMSMatches:
                        #if the specific "diagnosed in" appears before the year than no need for tie breaker, go with that year
                        diagnosedInRegex = "diagnosed\sin\s(19|20)\d{2}"
                        #re.search is different than re.findall in that it only looks for the first match and then returns out of it
                        #in order to read that match you access it with .group()
                        diagnosedInMatch = re.search(diagnosedInRegex, beforeMSMatch, re.IGNORECASE)
                        if(diagnosedInMatch):
                            #this is a hard return meaning that it calls the diagnosis year right here and now
                            #gets the last 4 letters of that match which we know from the regex it's the year
                            calledRecord.calledYear = diagnosedInMatch.group()[-4:]
                            calledRecord.calledText = beforeMSMatch
                            #we don't use hardCall here because we want this to be included with a common consensus
                            #year calculation made in identifyDiagnosisYear.py
                            return calledRecord


                    #special cases of wording. We completely return out if these specific wordings are found
                    specialMSRegex = r'(diagnosis\sof\s)((ms|multiplesclerosis|multiple\ssclerosis|))(\swas\smade\sin\s(19|20)\d{2})'
                    specialMSMatch = re.search(specialMSRegex, splitDiagnoseMatch, re.IGNORECASE)
                    if(specialMSMatch):
                        #this is a hard return meaning that it calls the diagnosis year right here and now
                        #gets the last 4 letters of that match which we know from the regex it's the year
                        calledRecord.calledYear = specialMSMatch.group()[-4:]
                        calledRecord.calledText = specialMSMatch.group()
                        #.hardCall = True is used in identifyDiagnosisYear.py to ignore finding a common consensus year
                        #and to just go with this year found here
                        calledRecord.hardCall = True
                        return calledRecord

                    specialMSRegex = r'diagnosed\swith\s(multiple\ssclerosis|MS|multiplesclerosis)\sin\s(19|20)\d{2}'
                    specialMSMatch = re.search(specialMSRegex, splitDiagnoseMatch, re.IGNORECASE)
                    if(specialMSMatch):
                        #this is a hard return meaning that it calls the diagnosis year right here and now
                        calledRecord.calledYear = specialMSMatch.group()[-4:]
                        calledRecord.calledText = specialMSMatch.group()
                        #.hardCall = True is used in identifyDiagnosisYear.py to ignore finding a common consensus year
                        #and to just go with this year found here
                        calledRecord.hardCall = True
                        return calledRecord



                    #search for any variation of MS in the sentence
                    regex =  r'multiple\ssclerosis|' \
                    + 'multiplesclerosis|' \
                    + '\sMS\s' \
                    + '|:MS\s' \
                    + '|\sMS\.(?!\s*\*\*NAME)' \
                    + '|:MS-'
                    MSFound = re.search(regex, splitDiagnoseMatch, re.IGNORECASE)
                    if(MSFound):
                        #if the phrase "Known Significant Medical Diagnoses and Conditions:" appears in the match
                        #make sure the year is in very close proximity to MS. This means we are in the header and
                        #we need to be careful that the year corresponds with the mention of MS
                        knownDiagnosesRegex = r'known\ssignificant\smedical\sdiagnoses\s'
                        knownDiagnosesMatch = re.search(knownDiagnosesRegex, splitDiagnoseMatch, re.IGNORECASE)
                        if(knownDiagnosesMatch):
                            knownMSMatch = re.search(self.smallerBoundsMSRegex, splitDiagnoseMatch, re.IGNORECASE)
                            if(knownMSMatch):
                                yearRegex = "(19|20|\')\d{2}"
                                specificYrMatch = re.search(yearRegex, knownMSMatch.group())
                                if(specificYrMatch):
                                    specificYr = specificYrMatch.group()

                                    #don't take a year after this certain phrase because it's going to be wrong. This section
                                    #follows the Known medical diagnoses section in many cases
                                    if(knownMSMatch.group().find("Operative and Invasive") > knownMSMatch.group().find(specificYr) or knownMSMatch.group().find("Operative and Invasive") == -1):

                                        #if the year is something like '94 we have to figure out if that means 1994 or 2094
                                        #milDecider takes the last two digits of current year
                                        milDecider = int(str(date.today().year)[-2:])
                                        if("'" in specificYr):
                                            #if the last two digits of the year are greater than the last two digits of the current year
                                            #then it's in the 1900's otherwise it's in the 2000's (Anything before 1916 would be classified as 2000's)
                                            if(int(specificYr[-2:]) > milDecider):
                                                specificYr = "19" + specificYr[-2:]
                                            else:
                                                specificYr = "20" + specificYr[-2:]

                                        calledRecord.calledYear = specificYr
                                        calledRecord.calledText = knownMSMatch.group()
                                        return calledRecord

                        #this particular split helps occasionally. It's a simpler version of splitting by sentence.
                        #In general, narrowing down the amount of text I searched for the diagnosis year helped
                        #reduce false positives
                        splitMSMatch = splitDiagnoseMatch.split('.')
                        for splitMatch in splitMSMatch:
                            #search for negating language
                            #look for negating language
                            negRegex = r'\sdoes\snot\s|\scan\'t\s|\swill\snot\s|\scannot\s|\scan\snot\s|\swon\'t\s|\sruledout\s|\sruled\sout\s'
                            negMatch = re.search(negRegex, splitMatch, re.IGNORECASE)

                            #if negating language is found than move on to the next sentence
                            if(negMatch):
                                continue

                            #This is another hard return. Looks for diagnosed in (year) within that sentence that also mentions MS
                            diagnosedInRegex = "diagnosed\sin\s(19|20)\d{2}"
                            diagnosedInMatch = re.search(diagnosedInRegex, splitMatch, re.IGNORECASE)
                            if(diagnosedInMatch):
                                #this is a hard return but we don't do a hard call which would automatically call the diagnosis year as this year
                                calledRecord.calledYear = diagnosedInMatch.group()[-4:]
                                calledRecord.calledText = splitMatch
                                return calledRecord

                            ### Relative date wording section ###
                            #The only relative wording that I found helpful was looking for
                            #years ago and then calling that year
                            yearsAgoRegex = r"(\d{1,2})\syears\sago"
                            newMatch = re.search(yearsAgoRegex, splitMatch, re.IGNORECASE)
                            if(newMatch):
                                yearsAgo = int(newMatch.group().split(' ')[0])
                                yearsAgoYr = entry_year - yearsAgo
                                calledMap = {'calledYear': str(yearsAgoYr), 'calledText': splitMatch}
                                yearMaps.append(calledMap)

                            ### Specific year section ###
                            #This section was much more helpful than relative wording. It looks for specific years
                            #mentioned in the same context as MS. This does it for each year in that sentence
                            yearRegex = ".{0,2}(19|20|\')\d{2}.{0,2}"
                            specificYrMatches = re.finditer(yearRegex, splitMatch, re.IGNORECASE)
                            for specificYrMatch in specificYrMatches:
                                #years inside [] or () in that same sentence were often not the right year
                                #because they were discussing something else
                                weedOutRegex = "\[|\]|\(|\)"
                                weedOutMatch = re.search(weedOutRegex, specificYrMatch.group(), re.IGNORECASE)
                                if(weedOutMatch):
                                    #If that was found, skip this year match
                                    continue

                                #if an s or an ' appears after the number, ignore it because it most likely is
                                #saying early/late in that decade(i.e. 1970s) which isn't specific enough

                                #gets the letter directly after the year
                                charAfterYr = specificYrMatch.group()[2:-1][-1:]
                                if(charAfterYr == '\'' or charAfterYr == 's'):
                                    continue

                                #we do the year regex again but this time just the year and not the characters before or after
                                #because at this point we know that the year is a real and specific year
                                yearRegex = "(19|20|\')\d{2}"
                                specificYr = re.search(yearRegex, specificYrMatch.group()).group()

                                #much like mentioned previously, we look for this phrase because it often
                                #threw us off track
                                if(splitMatch.find("Operative and Invasive") > splitMatch.find(specificYr) or splitMatch.find("Operative and Invasive") == -1):
                                    #if the year is something like '94 we have to figure out if that means 1994 or 2094
                                    #milDecider takes the last two digits of current year
                                    milDecider = int(str(date.today().year)[-2:])
                                    if("'" in specificYr):
                                        #if the last two digits of the year are greater than the last two digits of the current year
                                        #then it's in the 1900's otherwise it's in the 2000's (Anything before 1916 would be classified as 2000's)
                                        if(int(specificYr[-2:]) > milDecider):
                                            specificYr = "19" + specificYr[-2:]
                                        else:
                                            specificYr = "20" + specificYr[-2:]

                                    #search for dating back to language (doesn't find much)
                                    datesBackRegex = "dat[ie][nsd][g]?\sback\sto"
                                    dateMatch = re.search(datesBackRegex, splitMatch, re.IGNORECASE)
                                    if(dateMatch):
                                        calledMap = {'calledYear': str(specificYr), 'calledText': splitMatch}
                                        yearMaps.append(calledMap)

                                    #search for symptoms began language (doesn't find much)
                                    beganRegex = "(symptoms|symptom)\sbegan"
                                    beganMatch = re.search(beganRegex, splitMatch, re.IGNORECASE)
                                    if(beganMatch):
                                        calledMap = {'calledYear': str(specificYr), 'calledText': splitMatch}
                                        yearMaps.append(calledMap)

                                    #look for diagnos-ish words but ignore everything after the end of a sentence
                                    #this is a last ditch attempt to ensure we didn't miss anything by looking for any variation
                                    #of diagnosis again in the proximity of the year we found earlier
                                    splitMSMatch = splitMatch.split('.')
                                    for splitMatchDiag in splitMSMatch:
                                        diagnosRegex = "diagnos."
                                        diagnosMatch = re.search(diagnosRegex, splitMatchDiag, re.IGNORECASE)
                                        if(diagnosMatch):
                                            yearRegexCheck = re.search(specificYr, splitMatchDiag, re.IGNORECASE)
                                            if(yearRegexCheck):
                                                calledMap = {'calledYear': str(specificYr), 'calledText': splitMatch}
                                                yearMaps.append(calledMap)



            #if we found at least one diagnosis year in the record
            if(len(yearMaps) > 0):
                #find out the most common year repeated in this one record, ties are broken by later year
                yearMaps =  sorted(yearMaps, key=itemgetter('calledYear'), reverse=True)

                #this bit of code determines the most frequent diagnosis year used in this record
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

                #used to determine the accuracy of the algorithm since we don't have a
                #specified set of records to train from
                calledText = ""
                #construct all the text used to call this record
                for yearMap in yearMaps:
                    if(yearMap['calledYear'] == commonYr):
                        calledText += yearMap['calledText']
                        calledText += '\t'
                calledRecord.calledText = calledText

                #returning the called record is the same thing as saying that we found a diagnosis year in this record
                return calledRecord

        #when nothing else is found we return False since the record doesn't give a diagnosis year
        return False
