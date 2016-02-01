from __future__ import print_function
import datetime
import os.path
import sys
import re
import mysql.connector
from mysql.connector import errorcode

from rules.Rule import Rule
from rules.identifyDrugYearRules.ContextRule import ContextRule


#def run(records, finalRecords):
def run(records):
    contextRule = ContextRule("ContextRule")
    totalMeds = {}
    ruids = []

    #get a list of drugs per patient ruid
    # for finalRecord in finalRecords:
    #     if finalRecord.ruid not in ruids:
    #         ruids.append(finalRecord.ruid)

    #use a mocked out set of positives to speed testing up
    ruids = [
    7,
    10,
    67,
    68,
    69,
    71,
    72,
    74,
    75,
    79,
    80,
    101,
    109,
    119,
    194,
    195,
    196,
    197,
    199,
    200,
    201,
    202,
    203,
    205,
    210,
    212,
    213
    ]

    for ruid in ruids:
        totalMeds[ruid] = getMedRecords(ruid)


    #take each patient found in identify diagnosis year, check all their records to find the drugs
    i = 0
    length = len(records)
    for record in records:
        if record.ruid in totalMeds:
            for medName in totalMeds[record.ruid]:
                check = contextRule.run(record, medName)
            i += 1
            progress = round((i/length) * 100, 2)
            sys.stdout.write("Identifying drug dates... %d%%   \r" % (progress) )
            sys.stdout.flush()

def getMedRecords(ruid):
    meds = []
    try:
        cnx = mysql.connector.connect(user='suttons',
                                    password='gi*JOE=123',
                                    host='localhost',
                                    database='MFD_MS')
        cursor = cnx.cursor(prepared=True)
        #Training set pulled out here, just getting the first x  patients' records
        show_DB = "select  med from meds where ruid = " + str(ruid) + ";"
        cursor.execute(show_DB, multi=True)
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
