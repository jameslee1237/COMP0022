import mysql.connector
import pandas as pd
from mysql.connector import Error
#pdata = pd.read_csv(r"C:\Users\jlee0\Desktop\ml-latest-small\movies.csv", index_col=False, delimiter=',')
pdata = pd.read_csv(r"./movies.csv", index_col=False, delimiter=',')
pdata.head()

config = {
    'host': 'mysql',
    'port': 3306,
    'r_user': 'root',
    'r_pwd': '123',
    'user':'newuser',
    'password': '777',
    'database': 'testdb'
}




db_user = config.get('user')
db_pwd = config.get('password')
db_host = config.get('host')
db_port = config.get('port')
db_name = config.get('database')
db_ruser = config.get('r_user')
db_rpwd = config.get('r_pwd')

cnx = mysql.connector.connect(user=db_ruser, password=db_rpwd, host=db_host, port=db_port, database=db_name)

db_Info = cnx.get_server_info()
print("connected to mysql", db_Info)

cursor = cnx.cursor()
cursor.execute("select * FROM temp;")
temp = cursor.fetchall()

cursor.execute("CREATE DATABASE movies")
cursor.execute("GRANT ALL PRIVILEGES ON movies.* to 'newuser'@'%'")

cursor.close()
cnx.close()
print(temp)

cnx2 = mysql.connector.connect(user=db_user, password=db_pwd, host=db_host, port=db_port, database="movies")

cursor = cnx2.cursor()
cursor.execute("select database();")
record = cursor.fetchone()
print("connected to: ", record)
cursor.execute('DROP TABLE IF EXISTS moveis_data;')

cursor.execute("""CREATE TABLE movies_data(movie_ID INT NOT NULL AUTO_INCREMENT,
                                           title VARCHAR(255) NOT NULL,
                                           genre VARCHAR(255) NOT NULL,
                                           PRIMARY KEY(movie_ID));""")

for i, row in pdata.iterrows():
    if i == 0:
        print("INSERTING RECORDS")
    sql = "INSERT INTO movies.movies_data VALUES (%s, %s, %s)"
    cursor.execute(sql, tuple(row))
    cnx2.commit()
cursor.execute("select * FROM movies.movies_data WHERE movie_ID < 10;")
result = cursor.fetchall()

for i in result:
    print(i)

cursor.close()
cnx2.close()