from rules.Rule import Rule
import nltk
import nltk.data
import re
import difflib

class ContextRule(Rule):
    upperLimit = 75
    lowerLimit = 75
    samenessThreshold = .70

    def __init__(self, name):
        self.name = name

    #symtomList is a list of lists
    def run(self, record, symptomList, entry_year):
        #matches diagnosis, diagnosed, diagnos or multiple sclerosis or ms and returns the upperlimit amount of characters after and the lowerlimit of characters before
        regex = r'.{0,' + str(self.lowerLimit) + '}diagnos.{0,' + str(self.upperLimit) + '}'

        diagnoseMatches = re.findall(regex, record, re.IGNORECASE)

        #get year from entry_date
        years = []

        for diagnoseMatch in diagnoseMatches:
            #check for negating language here
            #TODO: Use negex package instead of the weak sauce below
            regex = r'\sno.\s|can\'t|cannot|negative'
            negMatches = re.findall(regex, diagnoseMatch)
            if(len(negMatches) == 0):
                regex = r'.{0,' + str(self.lowerLimit) + '}multiple\ssclerosis.{0,' + str(self.upperLimit) + '}|.{0,' + str(self.lowerLimit) + '}\sms\s.{0,' + str(self.upperLimit) + '}'
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
                    yearRegex = ".{0," + str(self.lowerLimit) + "}(19|20)\d{2}.{0," + str(self.upperLimit) + "}"
                    it = re.finditer(yearRegex, MSMatch, re.IGNORECASE)

                    for match in it:
                        #if DATE[] is in it, ignore it
                        weedOutRegex = "DATE\["
                        weedOutMatch = re.search(weedOutRegex, match.group(), re.IGNORECASE)
                        if(weedOutMatch):
                            continue

                        specificYrRegex = "(19|20)\d{2}"
                        specificYrMatch = re.search(specificYrRegex, match.group(), re.IGNORECASE)

                        if(specificYrMatch.group() != "" or specificYrMatch.group() is not None):
                            datesBackRegex = "dat[ie][nsd][g]?\sback\sto"
                            dateMatch = re.search(datesBackRegex, match.group(), re.IGNORECASE)
                            if(dateMatch):
                                years.append(specificYrMatch.group())

                            beganRegex = "(symptoms|symptom)\sbegan"
                            beganMatch = re.search(beganRegex, match.group(), re.IGNORECASE)
                            if(beganMatch):
                                years.append(specificYrMatch.group())

                            diagnosRegex = "diagnos."
                            diagnosMatch = re.search(diagnosRegex, match.group(), re.IGNORECASE)
                            if(diagnosMatch):
                                years.append(specificYrMatch.group())

                    if(len(years) < 1):
                        return False

                    #find out the most common year repeated, ties are broken by later year
                    years = sorted(years, key=int)

                    commonYr = 0000
                    count = 0
                    for year in years:
                        inLoopCount = 0
                        for yearOth in years:
                            if(year == yearOth):
                                inLoopCount += 1
                        if(inLoopCount > count):
                            count = inLoopCount
                            commonYr = year

                    return commonYr

        return False
