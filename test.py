import re
import mysql.connector
from mysql.connector import errorcode


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


meds = getMedRecords(219)
for medName in meds:
    recordContent = """---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| content                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **NAME[AAA BBB] VUH#: **ID-NUM **NAME[YYY M ZZZ] , M.D.**DATE[Jan 08 2007]HISTORY OF PRESENT ILLNESS: The patient is a **AGE[in 60s]-year-old female who returnsto clinic today for follow-up complaining of chiggers. She was working outin her yard over the weekend. She received multiple bites on the lowerextremities and upper extremities. She had issues in the past. She deniesany fevers, chills, or redness. PHYSICAL EXAMINATION: Examination reveals multiple inflamed papules on thelower extremities consistent with arthropod bites. No streaking or erythemato suggest cellulitis. No foul drainage. ASSESSMENT/PLAN: Insect bites consistent with chiggers. Started onover-the-counter Medrol Dosepak 60 mg IM times one. The patient's depressionis currently well-controlled. This has always relieved her chigger bitesthe best in the past. She will continue the Benadryl Dr. **NAME[XXX] put her on atnight with Pepcid for extreme itching.  **NAME[YYY M ZZZ] , M.D.JEP:MJTE/jdDD: **DATE[Jan 10 2007] 20:49DT: **DATE[Jan 11 2007] 13:31 |
+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------"""
    medNameReal = medName.decode("utf-8").strip()
    medRegex =  r'' + medNameReal
    print(medRegex)
    print(len(medRegex))
    medFinds = re.findall(medRegex, recordContent, re.IGNORECASE)
    print(medFinds)
