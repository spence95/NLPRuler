from Record import Record
from TrainingSetRecord import TrainingSetRecord
import mysql.connector
from mysql.connector import errorcode

class RecordsManager():
    username = ""
    password = ""
    connectionString = ""
    records = []
    trainingSetRecords = []
    trainingSetActualPositives = 0
    trainingSetActualNegatives = 0
    ruidLimit = 500

    def __init__(self, connectionString, username, password):
        self.connectionString = connectionString
        self.username = username
        self.password = password

    def getNextRecord(self, index):
        return self.records[index]

    def getTrainingSetRecords(self, fileName):
        try:
            cnx = mysql.connector.connect(user=self.username,
                                            password=self.password,
                                            host='localhost',
                                            database='MFD_MS')
            cursor = cnx.cursor(prepared=True)
        except mysql.connector.Error as err:
          if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
          elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
          else:
            print(err)

        with open(fileName) as inputfile:
            for line in inputfile:
                recordData = line.strip().split('\t')
                ruid = int(recordData[0].strip())
                isPositive = False
                if("true" in recordData[1]):
                    isPositive = True

                entry_date = recordData[2].strip()
                diagnosisYr = int(recordData[3])
                if(isPositive):
                    show_DB = "select content from notes where ruid =" + str(ruid) + " and entry_date = \"" + entry_date + "\";"
                    cursor.execute(show_DB, multi=True)
                    results = cursor.fetchall()
                    combinedNotes = ""
                    for result in results:
                        combinedNotes += str(result[0])

                    record = TrainingSetRecord(ruid, entry_date, combinedNotes)
                    record.isPositive = isPositive
                    record.diagnosisYr = diagnosisYr
                    self.trainingSetRecords.append(record)
                else:
                    show_DB = "select content from notes where ruid =" + str(ruid) + ";"
                    cursor.execute(show_DB, multi=True)
                    results = cursor.fetchall()
                    combinedNotes = ""
                    for result in results:
                        record = TrainingSetRecord(ruid, entry_date, str(result[0]))
                        record.isPositive = isPositive
                        record.diagnosisYr = diagnosisYr
                        self.trainingSetRecords.append(record)

        return self.trainingSetRecords

    #used in running against unknown diagnosis records
    def getAllRecords(self):
        #open the connection
        try:
            cnx = mysql.connector.connect(user=self.username,
                                        password=self.password,
                                        host='localhost',
                                        database='MFD_MS')
            cursor = cnx.cursor(prepared=True)
            #Training set pulled out here, just getting the first x  patients' records
            show_DB = "select  ruid, entry_date, content from notes where ruid in (Select * from (select distinct ruid from notes Limit 200) as t);"
            #show_DB = "select ruid, entry_date, content from notes where (ruid = 383)"
            cursor.execute(show_DB, multi=True)
            results = cursor.fetchall()
            for result in results:
                ruid = result[0]
                date = result[1]
                content = result[2]
                record = Record(ruid, date, content)
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

    def getRecordsForRuid(ruid, sqlStatement):
        meds = []
        try:
            cnx = mysql.connector.connect(user=self.username,
                                        password=self.password,
                                        host='localhost',
                                        database='MFD_MS')
            cursor = cnx.cursor(prepared=True)
            #Training set pulled out here, just getting the first x  patients' records

            cursor.execute(sqlStatement, multi=True)
            results = cursor.fetchall()
            for result in results:
                meds.append(result[0])

        except mysql.connector.Error as err:
          if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
          elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
          else:
            print(err)
        else:
          cnx.close()

        return meds
