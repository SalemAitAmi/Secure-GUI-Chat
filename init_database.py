#!/usr/bin/python3
import sqlite3
from db_management import ChatDatabase

"""
Database Structure:
    user_table: Contains the usernames and hashed passwords for all registered users
    conversation_user1_user2: Contains all messages sent between 2 users in chronological order in the following form:  (Sender | message | timestamp) 
"""


if __name__ == '__main__':
    conn = sqlite3.connect('chat_database')
    c = conn.cursor()

    try:
        c.execute('''
            CREATE TABLE `user_table` (
            `username` varchar(256) NOT NULL,
            `password` varchar(256) NOT NULL,
            PRIMARY KEY (`username`)
            )
                    ''')
        c.execute(f'''
        INSERT INTO `user_table` VALUES 
        ('Alice','alice'),
        ('Boby','boby'),
        ('Ryan','ryan'),
        ('Samy','Samy'),
        ('Ted','ted'),
        ('Admin','admin')
                ''')
        print("Database Initialized!")
    except Exception:
        print("user_table already exists!")

    conn.commit()