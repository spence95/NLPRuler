from rules.Rule import Rule
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
        #matches diagnosis, diagnosed, diagnos or multiple sclerosis or ms and returns the upperlimit amount of characters after and the lowerlimit of characters before
        regex = r'.{0,' + str(self.lowerLimit) + '}diagnos.{0,' + str(self.upperLimit) + '}'

        diagnoseMatches = re.findall(regex, record, re.IGNORECASE)
        MSMatches = []

        #get year from entry_date
        years = []

        for diagnoseMatch in diagnoseMatches:
            #check for negating language here
            #TODO: Use negex package instead of the weak sauce below
            regex = r'\sno.\s|can\'t|cannot|negative|possible'
            negMatches = re.findall(regex, diagnoseMatch, re.IGNORECASE)
            if(len(negMatches) == 0):
                regex = r'.{0,' + str(self.lowerLimit) + '}multiple\ssclerosis.{0,' + str(self.upperLimit) + '}|.{0,' \
                + str(self.lowerLimit) + '}multiplesclerosis.{0,' + str(self.upperLimit) + '}|.{0,' \
                + str(self.lowerLimit) + '}\sMS\s.{0,' + str(self.upperLimit) + '}' \
                + '|.{0,' + str(self.lowerLimit) + '}:MS\s.{0,' + str(self.upperLimit) + '}' \
                + '|.{0,' + str(self.lowerLimit) + '}\sMS\..{0,' + str(self.upperLimit) + '}'
                MSMatches = re.findall(regex, diagnoseMatch, re.IGNORECASE)
                for MSMatch in MSMatches:
                    ### Relative date wording section ###
                    yearsAgoRegex = "/(\d{1,2})\s+years\s+ago/"
                    newMatch = re.search(yearsAgoRegex, MSMatch, re.IGNORECASE)
                    if(newMatch):
                        yearsAgo = int(newMatch.split(' ')[0])
                        yearsAgoYr = entry_year - yearsAgo
                        years.append(yearsAgoYr)

                    #TODO: last year

                    ### Specific year section ###
                    yearRegex = ".{0,2}(19|20)\d{2}.{0,2}"
                    specificYrMatches = re.finditer(yearRegex, MSMatch, re.IGNORECASE)
                    for specificYrMatch in specificYrMatches:
                        #if DATE[] is in it, ignore it
                        weedOutRegex = "\[|\]"
                        weedOutMatch = re.search(weedOutRegex, specificYrMatch.group(), re.IGNORECASE)
                        if(weedOutMatch):
                            continue

                        #take first two and last two chars off of year match
                        specificYr = specificYrMatch.group()[2:-2]

                        datesBackRegex = "dat[ie][nsd][g]?\sback\sto"
                        dateMatch = re.search(datesBackRegex, MSMatch, re.IGNORECASE)
                        if(dateMatch):
                            years.append(specificYr)

                        beganRegex = "(symptoms|symptom)\sbegan"
                        beganMatch = re.search(beganRegex, MSMatch, re.IGNORECASE)
                        if(beganMatch):
                            years.append(specificYr)

                        #look for diagnos-ish words but ignore everything after the end of a sentence
                        splitMSMatch = MSMatch.split('.')
                        for splitMatch in splitMSMatch:
                            diagnosRegex = "diagnos."
                            diagnosMatch = re.search(diagnosRegex, splitMatch, re.IGNORECASE)
                            if(diagnosMatch):
                                yearRegexCheck = re.search(specificYr, splitMatch, re.IGNORECASE)
                                if(yearRegexCheck):
                                    years.append(specificYr)




            if(len(MSMatches) > 0):
                #if the specific "diagnosed in" appears before the year than no need for tie breaker, go with that year
                diagnosedInRegex = "diagnosed\sin\s(19|20)\d{2}"
                diagnosedInMatch = re.search(diagnosedInRegex, record, re.IGNORECASE)
                if(diagnosedInMatch):
                    return diagnosedInMatch.group()[-4:]



            if(len(years) > 0):
                #find out the most common year repeated, ties are broken by later year
                years = sorted(years, key=int)

                commonYr = 0000
                count = 0
                for year in reversed(years):
                    inLoopCount = 0
                    for yearOth in reversed(years):
                        if(year == yearOth):
                            inLoopCount += 1
                    if(inLoopCount > count):
                        count = inLoopCount
                        commonYr = year

                return commonYr





        return False
