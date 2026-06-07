import pymysql

def get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='root',       
        password='',         
        database='roderick_cafe_db',
        cursorclass=pymysql.cursors.DictCursor
    )