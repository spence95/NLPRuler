from rules.Rule import Rule
import nltk
import nltk.data
import re
import difflib

class ImpressionRule(Rule):
    impressionLimit = 250
    diagnosesLimit = 50
    lowerLimit = 120
    upperLimit = 120

    years = []

    def __init__(self, name):
        self.name = name

    def run(self, record, entry_year):
        msRegex = r'multiple\ssclerosis|multiplesclerosis|\sms\s|:ms\s'
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
                        #at this point, the patient has MS, this only picks out the ones being presently diagnosed
                        diagnosRegex = r'.{0,' + str(self.lowerLimit) + '}diagnos.{0,' + str(self.upperLimit) + '}'
                        diagnosMatch = re.search(diagnosRegex, impressionMatch.group(), re.IGNORECASE)

                        # for diagnosMatch in diagnosMatches:
                        #     #look for year and past diagnosis language, if not there,
                        #     #previous regex shows that the doctor is presently diagnosedInRegex
                        #     ### Specific year section ###
                        #     yearRegex = ".{0,2}(19|20)\d{2}.{0,2}"
                        #     specificYrMatches = re.finditer(yearRegex, diagnosMatch, re.IGNORECASE)
                        #     for specificYrMatch in specificYrMatches:
                        #         #if DATE[] is in it, ignore it
                        #         weedOutRegex = "\[|\]"
                        #         weedOutMatch = re.search(weedOutRegex, specificYrMatch.group(), re.IGNORECASE)
                        #         if(weedOutMatch):
                        #             continue
                        #
                        #         #take first two and last two chars off of year match
                        #         specificYr = specificYrMatch.group()[2:-2]
                        #
                        #         datesBackRegex = "dat[ie][nsd][g]?\sback\sto"
                        #         dateMatch = re.search(datesBackRegex, diagnosMatch, re.IGNORECASE)
                        #         if(dateMatch):
                        #             years.append(specificYr)
                        #
                        #         beganRegex = "(symptoms|symptom)\sbegan"
                        #         beganMatch = re.search(beganRegex, diagnosMatch, re.IGNORECASE)
                        #         if(beganMatch):
                        #             years.append(specificYr)
                        #
                        #         diagnosRegex = "diagnos."
                        #         diagnosMatch = re.search(diagnosRegex, diagnosMatch, re.IGNORECASE)
                        #         if(diagnosMatch):
                        #             years.append(specificYr)
                        #
                        #         if(len(years) > 0):
                        #             #find out the most common year repeated, ties are broken by later year
                        #             years = sorted(years, key=int)
                        #
                        #             commonYr = 0000
                        #             count = 0
                        #             for year in reversed(years):
                        #                 inLoopCount = 0
                        #                 for yearOth in reversed(years):
                        #                     if(year == yearOth):
                        #                         inLoopCount += 1
                        #                 if(inLoopCount > count):
                        #                     count = inLoopCount
                        #                     commonYr = year
                        #
                        #             return str(commonYr)
                        if(diagnosMatch):
                            return str(entry_year)

        return False
