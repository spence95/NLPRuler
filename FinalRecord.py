from Record import Record

class FinalRecord():
    def __init__(self):
        self.ruid = 0
        self.diagnosisYr = 0
        #dict of drugs with a 2 size list composed of start date and end date for that respective drug
        self.drugs = {}
        self.symptoms = {}
