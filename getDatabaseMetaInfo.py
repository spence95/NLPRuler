from __future__ import print_function
import mysql.connector
from mysql.connector import errorcode

def getDatabaseMetaInfo():
    #connect to db
    try:
        cnx = mysql.connector.connect(user='suttons',
                                    password='gi*JOE=123',
                                    host='localhost',
                                    database='MFD_MS')
        cursor = cnx.cursor(prepared=True)
        #columns are ruid, doc_type, sub_type, entry_date, content, doc_id, part_num, grouper
        show_DB = "select * from notes where ruid < 200;"
        cursor.execute(show_DB, multi=True)
        results = cursor.fetchall()

        f = open("dbSet.txt", 'w')
        for result in results:
            string = str(result) + "\t"
            print(string, file = f)



    except mysql.connector.Error as err:
      if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with your user name or password")
      elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
      else:
        print(err)
    else:
      cnx.close()

getDatabaseMetaInfo()
