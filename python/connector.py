import mysql.connector as mysql
import time
from datetime import datetime, timedelta
from jwcrypto import jwt, jwk

HOST = "tp2-db"
DATABASE = "authentication"
USER = "root"
PASSWORD = "root"


class Connector:
    def __init__(self):
        connected = False
        while(not connected):
            try:
                self.db_connection = mysql.connect(host=HOST, database=DATABASE, user=USER, password=PASSWORD)
                connected = True
            except:
                print("Waiting for DB to come online")
                time.sleep(3)

        self.key = jwk.JWK(generate='oct', size=256)

    def generateToken(self, user):
        token = jwt.JWT(header={"alg": "HS256"},
                        claims={"user": user,
                                "time": str(datetime.now())})
        token.make_signed_token(self.key)
        return token.serialize()


    def insertUser(self, user, password, admin):
        cursor = self.db_connection.cursor()
        add = ("INSERT INTO tokens "
               "(token, user, password, tokenTime, admin) "
               "VALUES (%s, %s, %s, %s, %s)")

        data = (self.generateToken(user), user, password, datetime.now(), admin)

        cursor.execute(add, data)
        self.db_connection.commit()
        cursor.close()

    def logout(self, user):
        cursor = self.db_connection.cursor()
        query = ("UPDATE tokens "
                 "SET tokenTime=%s"
                 "WHERE user=%s")

        data = (datetime.now() - timedelta(hours = 1), user)

        cursor.execute(query, data)
        self.db_connection.commit()
        cursor.close()


    def updateTokenTime(self, token, user):
        cursor = self.db_connection.cursor()
        query = ("UPDATE tokens "
                 "SET tokenTime=%s"
                 "WHERE token=%s AND user=%s")

        data = (datetime.now(), token, user)

        cursor.execute(query, data)
        self.db_connection.commit()
        cursor.close()


    def updateToken(self, token, user):
        cursor = self.db_connection.cursor()
        query = ("UPDATE tokens "
                 "SET token=%s, tokenTime=%s"
                 "WHERE user=%s")

        data = (token, datetime.now(), user)

        cursor.execute(query, data)
        self.db_connection.commit()
        cursor.close()

    def checkForUser(self, user):
        cursor = self.db_connection.cursor()
        query = ("SELECT user FROM tokens WHERE user = %s")

        cursor.execute(query, (user, ))

        returnedUser = ""
        for(ruser) in cursor:
            returnedUser = ruser;

        cursor.close()

        if returnedUser != "":
            return True
        else:
            return False

    def checkToken(self, token, user):
        cursor = self.db_connection.cursor()
        query = ("SELECT token, tokenTime FROM tokens WHERE user = %s")

        cursor.execute(query, (user, ))

        returnedToken = ""
        returnedTime = ""
        for(rtoken, rtokenTime) in cursor:
            returnedToken = rtoken;
            returnedTime = rtokenTime

        cursor.close()

        if token == returnedToken and (datetime.now() - returnedTime).total_seconds() < 300:
            return True
            self.updateTokenTime(token, user)
        else:
            return False

    def checkAdmin(self, user):

        cursor = self.db_connection.cursor()
        query = ("SELECT admin FROM tokens WHERE user = %s")

        cursor.execute(query, (user, ))

        returnedAdmin = ""
        for(rAdmin) in cursor:
            returnedAdmin = rAdmin;

        cursor.close()

        return returnedAdmin


    def getToken(self, user, password):
        cursor = self.db_connection.cursor()
        query = ("SELECT user, password, token, tokenTime FROM tokens WHERE user = %s")

        cursor.execute(query, (user, ))

        returnedUser = ""
        returnedPassword = ""
        returnedToken = ""
        returnedTime = ""
        for(ruser, rpassword, rtoken, rtime) in cursor:
            returnedUser = ruser
            returnedPassword = rpassword
            returnedToken = rtoken
            returnedTime = rtime

        if user == returnedUser and password == returnedPassword:
            if (datetime.now() - returnedTime).total_seconds() < 300:
                self.updateTokenTime(returnedToken, user)
                return returnedToken
            else:
                token = self.generateToken(user)
                self.updateToken(token, user)
                return token
        else:
            return False
