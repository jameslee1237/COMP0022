import mysql.connector
import pandas as pd
from mysql.connector import Error
from flask import Flask

app = Flask(__name__)

class App:
    def __init__(self):
        self.rconnected = False
        self.nconnected = False
        self.config = {}
        self.pdata = ""

    def set_config(self):
        self.config = {'host': 'mysql',
                       'port': 3306,
                       'r_user': 'root',
                       'r_pwd': '123',
                       'user':'newuser',
                       'password': '777',
                       'database': 'testdb'
                      }
    def get_csv_data(self):
        self.pdata = pd.read_csv(r"./movies.csv", index_col=False, delimiter=',')
        self.pdata.head()

    def connect_with_root(self):
        db_host = self.config.get('host')
        db_port = self.config.get('port')
        db_name = self.config.get('database')
        db_ruser = self.config.get('r_user')
        db_rpwd = self.config.get('r_pwd')
        self.cnx = mysql.connector.connect(user=db_ruser, password=db_rpwd, host=db_host, port=db_port, database=db_name)
        db_Info = self.cnx.get_server_info()
        print("connected to mysql", db_Info)
        self.rconnected = True

    def grant_prev(self):
        if self.rconnected != True:
            print("please make a connection first")
            exit()
        else:
            cursor = self.cnx.cursor()
            cursor.execute("CREATE DATABASE IF NOT EXISTS movies;")
            cursor.execute("GRANT ALL PRIVILEGES ON movies.* to 'newuser'@'%'")
            cursor.close()
    
    def close_connec_root(self):
        if self.rconnected != False:
            self.cnx.close()
            self.rconnected = False
        else:
            print("connection is already closed")
        
    def connect_newuser(self, db_name):
        db_user = self.config.get('user')
        db_pwd = self.config.get('password')
        db_host = self.config.get('host')
        db_port = self.config.get('port')
        self.cnx2 = mysql.connector.connect(user=db_user, password=db_pwd, host=db_host, port=db_port, database=db_name)
        self.nconnected = True
    
    def create_table_with_data(self):
        cursor = self.cnx2.cursor()
        cursor.execute("select database();")
        record = cursor.fetchone()
        print("connected to: ", record)
        cursor.execute('DROP TABLE IF EXISTS movies_data;')
        cursor.execute("""CREATE TABLE movies_data(movie_ID INT NOT NULL AUTO_INCREMENT,
                                           title VARCHAR(255) NOT NULL,
                                           genre VARCHAR(255) NOT NULL,
                                           PRIMARY KEY(movie_ID));""")

        for i, row in self.pdata.iterrows():
            if i == 0:
                print("INSERTING RECORDS")
            sql = "INSERT INTO movies.movies_data VALUES (%s, %s, %s)"
            cursor.execute(sql, tuple(row))
            self.cnx2.commit()
        cursor.close()

    def print_first_10_terminal(self):
        result = self.print_first_10()
        for i in result:
            print(i)
        

    def print_first_10(self):
        cursor = self.cnx2.cursor()
        cursor.execute("select * FROM movies.movies_data WHERE movie_ID < 10;")
        result = cursor.fetchall()
        cursor.close()
        return result
    
    def close_nconnect(self):
        self.cnx2.close()

@app.route("/")
def get_data():
    app1 = App()
    app1.set_config()
    app1.get_csv_data()
    try:
        app1.connect_with_root()
    except Error as e:
        print("Error while connecting: ", e)
    if app1.rconnected != False:
        app1.grant_prev()
        app1.close_connec_root()
    try:
        app1.connect_newuser("movies")
    except Error as e:
        print("Error while connecting: ", e)
    if app1.nconnected != False:
        app1.create_table_with_data()
        app1.print_first_10_terminal()
        data = app1.print_first_10()
        app1.close_nconnect()
    return data

if __name__ == "__main__":
    app.run(debug=True)