from Record import Record

class CalledRecordDiagnoseYr(Record):
    #parent class columns are ruid, doc_type, sub_type, entry_date, content, doc_id, part_num, grouper
    calledYear = 0000
    #Called text is the snippet of text that made us call the year we did
    calledText = ""
    calledRule = ""
    #hardCall is used to skip all other indicators for a year since the one we just found is perfect.
    hardCall = False
