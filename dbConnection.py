import mysql.connector
from mysql.connector import errorcode

class DBConnection():
    cursor = ""

    def get(self):
        if(self.cursor == ""):
            try:
                self.cnx = mysql.connector.connect(user='suttons',
                                            password='gi*JOE=123',
                                            host='localhost',
                                            database='MFD_MS')
                self.cursor = self.cnx.cursor(prepared=True)

            except mysql.connector.Error as err:
              if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
              elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
              else:
                print(err)
            else:
              self.cnx.close()

            return self.cursor
        else:
            return self.cursor

    def close(self):
        cnx.close()
