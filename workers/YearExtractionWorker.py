from workers.Worker import Worker
import re

class YearExtractionWorker(Worker):

    def work(self, record, recordYr):
        yearsAgoRegex = "/(\d{1,2})\s+years\s+ago/"
        match = re.search(yearsAgoRegex, record, re.IGNORECASE)
        if(match)
            yearsAgo = int(match.group().split(' ')[0])
            recordYr -= yearsAgo
            return recordYr

        datesBackRegex = "/dat[ie][nsd][g]?\sback\sto(.*?)(\d\d\d\d)/"
        match = re.search(datesBackRegex, record, re.IGNORECASE)
        if(match)
            recordYr = int(match.group()[-4:])
            return recordYr

        return recordYr
