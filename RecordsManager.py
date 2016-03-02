from Record import Record
import mysql.connector
from mysql.connector import errorcode
'''
RecordsManager accesses the underlying MySQL database and transforms that data into
Python objects that the script can work with. It requires mysql.connector to be installed
on the machine you run the script. This can be found here: https://dev.mysql.com/downloads/connector/python/.
Much of the code found here was patterned after this example:
https://dev.mysql.com/doc/connector-python/en/connector-python-example-connecting.html.
'''
class RecordsManager():
    username = ""
    password = ""
    connectionString = ""
    records = []
    database= 'MFD_MS'
    host = 'localhost'


    def __init__(self, connectionString, username, password):
        self.connectionString = connectionString
        self.username = username
        self.password = password

    #runs a custom query against the database and returns record objects
    def getAllRecords(self):
        #open the connection
        try:
            cnx = mysql.connector.connect(user=self.username,
                                        password=self.password,
                                        host=self.host,
                                        database=self.database)
            cursor = cnx.cursor(prepared=True)
            #Training set pulled out here, just getting the first x  patients' records, when grouper = 5 it means patient does not have MS
            #This is a subquery, the inside query makes a list of ruids from the first 200 patients in the DB then the outer query gets every
            #record for each of those ruids
            show_DB = """select  ruid, entry_date, content from notes where ruid in
            (Select * from (select distinct ruid from notes where grouper != 5 order by ruid, entry_date Limit 200) as t);"""
            cursor.execute(show_DB, multi=True)
            results = cursor.fetchall()
            #converts each result to a record object
            for result in results:
                ruid = result[0]
                date = result[1]
                content = result[2]
                record = Record(ruid, date, content)
                #appends to records attribute then to be used elsewhere
                self.records.append(record)

        except mysql.connector.Error as err:
          if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
          elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
          else:
            print(err)
        else:
          cnx.close()

    def getDrugRecords(self):
        results = []
        try:
            cnx = mysql.connector.connect(user=self.username,
                                        password=self.password,
                                        host='localhost',
                                        database='MFD_MS')
            cursor = cnx.cursor(prepared=True)
            #Training set pulled out here, just getting the first x  patients' records
            # sqlStatement = "Select ruid, entry_date, content from notes where doc_type != 'PL' and sub_type not like '%PROBLEM%'"
            sqlStatement = "select  ruid, entry_date, content from notes where ruid in (Select * from (select distinct ruid from notes where grouper != 5 and doc_type != 'PL' and sub_type not like '%PROBLEM%' order by ruid, entry_date Limit 200) as t);"
            cursor.execute(sqlStatement, multi=True)
            dbResults = cursor.fetchall()
            for result in dbResults:
                record = Record(result[0], result[1], result[2])
                results.append(record)

        except mysql.connector.Error as err:
          if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
          elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
          else:
            print(err)
        else:
          cnx.close()

        return results
