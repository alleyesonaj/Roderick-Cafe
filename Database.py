import pymysql

def get_db_connection():
    """
    Establishes a connection to the local XAMPP MySQL database server instance.
    Defaults use 'root' with an empty password configuration.
    """
    return pymysql.connect(
        host='localhost',
        user='root',       
        password='',         
        database='rodCafe_db',
        cursorclass=pymysql.cursors.DictCursor
    )