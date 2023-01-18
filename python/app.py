import mysql.connector


config = {
    'host': 'mysql',
    'port': 3306,
    'user':'newuser',
    'password': '777',
    'database': 'testdb'
}


db_user = config.get('user')
db_pwd = config.get('password')
db_host = config.get('host')
db_port = config.get('port')
db_name = config.get('database')

cnx = mysql.connector.connect(user=db_user, password=db_pwd, host=db_host, port=db_port, database=db_name)

db_Info = cnx.get_server_info()
print("connected to mysql", db_Info)

cursor = cnx.cursor()
cursor.execute("select * FROM temp;")
temp = cursor.fetchall()

cursor.close()
cnx.close()
print(temp)