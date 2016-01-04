from rules.Rule import Rule
import re
import difflib

class YearExtractionRule(Rule):
    upperLimit = 150
    lowerLimit = 150

    def __init__(self, name):
        self.name = name

    def run(self, record, recordYr):
        '''
        yearsAgoRegex = "/(\d{1,2})\s+years\s+ago/"
        match = re.search(yearsAgoRegex, record, re.IGNORECASE)
        if(match):
            yearsAgo = int(match.group().split(' ')[0])
            recordYr -= yearsAgo
            return True
        '''

        yearRegex = ".{0," + str(self.lowerLimit) + "}(19|20)\d{2}.{0," + str(self.upperLimit) + "}"
        matches = re.search(yearRegex, record, re.IGNORECASE)
        it = re.finditer(yearRegex, record, re.IGNORECASE)

        for match in it:
            regex = r'multiple\ssclerosis|\sms\s}'
            matches = re.findall(regex, match.group(), re.IGNORECASE)
            if(len(matches) < 1):
                continue

            specificYrRegex = "(19|20)\d{2}"
            specificYrMatch = re.search(specificYrRegex, match.group(), re.IGNORECASE)

            #if DATE[] is in it, ignore it
            weedOutRegex = "DATE\["
            weedOutMatch = re.search(weedOutRegex, match.group(), re.IGNORECASE)
            if(weedOutMatch):
                continue

            weedOutRegex = "Medical\sDiagnoses\sand\sConditions"
            weedOutMatch = re.search(weedOutRegex, match.group(), re.IGNORECASE)
            if(weedOutMatch):
                continue
                
            print(match.group())
            datesBackRegex = "dat[ie][nsd][g]?\sback\sto"
            dateMatch = re.search(datesBackRegex, match.group(), re.IGNORECASE)
            if(dateMatch):
                with open("yearMatchesOutput.txt", "a") as myfile:
                    string = match.group() + "\n"
                    myfile.write(string)
                return specificYrMatch

            '''
            startedRegex = "started"
            startedMatch = re.search(startedRegex, match.group(), re.IGNORECASE)
            if(startedMatch):
                return True
            '''

            beganRegex = "(symptoms|symptom)\sbegan"
            beganMatch = re.search(beganRegex, match.group(), re.IGNORECASE)
            if(beganMatch):
                with open("yearMatchesOutput.txt", "a") as myfile:
                    string = match.group() + "\n"
                    myfile.write(string)
                return specificYrMatch

            diagnosRegex = "diagnos."
            diagnosMatch = re.search(diagnosRegex, match.group(), re.IGNORECASE)
            if(diagnosMatch):
                with open("yearMatchesOutput.txt", "a") as myfile:
                    string = match.group() + "\n"
                    myfile.write(string)
                return specificYrMatch

        return False
