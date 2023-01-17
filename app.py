import mysql.connector


config = {
    'host': 'localhost',
    'port': 3306,
    'user':'newuser',
    'password': '777',
    'database': 'mydb'
}

db_user = config.get('user')
db_pwd = config.get('password')
db_host = config.get('host')
db_port = config.get('port')
db_name = config.get('database')


cnx = mysql.connector.connect(host=db_host, user=db_user, password=db_pwd, db=db_name)
db_Info = cnx.get_server_info()
print("connected to mysql", db_Info)

cursor = cnx.cursor()
cursor.execute(f'use {db_name};')
#cursor.execute("CREATE TABLE movies(title VARCHAR(50) NOT NULL,genre VARCHAR(30) NOT NULL,director VARCHAR(60) NOT NULL,release_year INT NOT NULL,PRIMARY KEY(title));")
cursor.execute('INSERT INTO movies VALUE ("Joker", "psychological thriller", "Todd Phillips", 2019);')
cursor.execute('SELECT * FROM movies')
record = cursor.fetchall()

print(record)

cursor.close()
cnx.close()