from connector import Connector
import mysql.connector as mysql
from datetime import datetime




if __name__ == "__main__":
    HOST = "tp2-db"
    DATABASE = "authentication"
    USER = "root"
    PASSWORD = "root"
    db_connection = mysql.connect(host=HOST, database=DATABASE, user=USER, password=PASSWORD)
    connector = Connector()
    connector.insertUser("pedro", "pedro", True)
