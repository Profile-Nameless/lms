import mysql.connector

def create_db_connection():
    conn = mysql.connector.connect(host= "localhost",
                                   user="root",
                                   password="admin1234",
                                   database="gravity_books")
    cursor = conn.cursor(dictionary=True)
    return conn, cursor





create_db_connection()