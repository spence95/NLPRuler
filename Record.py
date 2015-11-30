class Record():
    #columns are ruid, doc_type, sub_type, entry_date, content, doc_id, part_num, grouper
    ruid = -1
    doc_type = ""
    sub_type = ""
    entry_date = ""
    content = ""
    doc_id = -1
    part_num = -1
    grouper = -1

    def __init__(self, ruid, date, content):
        self.ruid = ruid
        #self.doc_type = doc_type
        #self.sub_type = sub_type
        self.entry_date = date
        self.content = str(content)
