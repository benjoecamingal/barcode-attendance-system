import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",  # Change if using a different MySQL user
        password="",  # Add your MySQL password
        database="attendance_db"
    )
