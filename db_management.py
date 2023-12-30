#!/usr/bin/python3
import sqlite3
# Table Format:
#   Table Name: conversation_user1_user2
#   Table Columns: (line_num) (sender) (message)
# For each table, conversation_user1_user2 there is an equivalent conversation_user2_user1
# Create user_table for storing credentials (i.e. (userName, (passWord)))

# NOTE: MySQL connector syntax
# mydb = connectUser("root", "password123")
# mycursor = mydb.cursor()
# mycursor.execute("CREATE TABLE conversation_1 (line_num INT AUTO_INCREMENT PRIMARY KEY, sender VARCHAR(30) NOT NULL, message TEXT NOT NULL)")
# CREATE TABLE user_table (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(30) NOT NULL, passwd VARCHAR(30) NOT NULL);
# querry = "INSERT INTO conversation_1 (sender, message) VALUES (%s, %s)"
# param = ("World", "Hello John!")
# mycursor.execute(query, param)
# mydb.commit()
class ChatDatabase:
    def __init__(self, database_name):
        # Establish database connection
        self.db_conn = sqlite3.connect(database_name)
        try: 
            self.db_conn.cursor()
        except:
            print("Error initializing cursor, exiting!")
            exit(1)
    
    def addUser(self, username, password):
        cursor = self.db_conn.cursor()
        cursor.execute("SELECT * FROM user_table WHERE username=?", (username,))
        if(cursor.fetchall()):
            print("User already exists!")
            return False
        cursor.execute("INSERT INTO user_table (username, password) VALUES (?, ?)", (username, password))
        self.db_conn.commit()
        print(f"{username} registered!")
        return True
    
    def getUser(self, username):
        cursor = self.db_conn.cursor()
        cursor.execute("SELECT * FROM user_table WHERE username=?", (username,))
        result = cursor.fetchone()
        return result
    
    def getAllUsers(self):
        cursor = self.db_conn.cursor()
        cursor.execute("SELECT * FROM user_table")
        result = cursor.fetchall()
        return result
    
    def getAllTables(self):
        cursor = self.db_conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        table_list = cursor.fetchall()
        return table_list


    def getConversation(self, user1, user2):
        cursor = self.db_conn.cursor()
        # Check if the conversation  exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        table_list = cursor.fetchall()
        shape1 = table_list.count(("conversation_"+user1+"_"+user2,))
        shape2 = table_list.count(("conversation_"+user2+"_"+user1,))
        if shape1:
            cursor.execute(f"SELECT * FROM conversation_"+user1+"_"+user2)
        elif shape2:
            cursor.execute(f"SELECT * FROM conversation_"+user2+"_"+user1)
        else:
            print("Conversation does not exists!")
            return None

        result = cursor.fetchall()
        return result

    def createConversation(self, user1, user2):
        """
        Create a new conversation between existing users.
        """
        cursor = self.db_conn.cursor()
        # Check if the conversation already exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        table_list = cursor.fetchall()
        if table_list.count(("conversation_"+user1+"_"+user2,)) or table_list.count(("conversation_"+user2+"_"+user1,)):
            print("Conversation already exists!")
            return

        # Check if both users exist in the database
        cursor.execute("SELECT username FROM user_table")
        user_list = cursor.fetchall()
        if user_list.count((user1,)) == 0:
            print(f"{user1} is not registered!")
            return
        if user_list.count((user2,)) == 0:
            print(f"{user2} is not registered!")
            return

        # Query text
        query = "CREATE TABLE conversation_"+user1+"_"+user2+" (sender VARCHAR(300) NOT NULL, message TEXT NOT NULL, timestamp INTEGER PRIMARY KEY)"

        # Only create a new conversation table if one isn't already active
        if table_list.count(("conversation_"+user1+"_"+user2,)) == 0:
            cursor.execute(query)
    
        self.db_conn.commit()
        print(f"Conversation between {user1} and {user2} created!")
        return True

    def appendConversation(self, sender : str, receiver : str, message : str):
        """
        Append an existing conversation with a new message.
        Return 1 on success, 0 otherwise.
        """
        if not len(message) > 0:
            return 0

        cursor = self.db_conn.cursor()
        # Check if conversation exists and assert shape of query
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        table_list = cursor.fetchall()
        if table_list.count(("conversation_"+sender+"_"+receiver,)) != 0:
            query = "INSERT INTO conversation_"+sender+"_"+receiver+" (sender, message) VALUES (?, ?)"
            cursor.execute(query, (sender, message))
        elif table_list.count(("conversation_"+receiver+"_"+sender,)) != 0:
            query = "INSERT INTO conversation_"+receiver+"_"+sender+" (sender, message) VALUES (?, ?)"
            cursor.execute(query, (sender, message))
        else:
            print(f"Conversation between {sender} & {receiver} does not exist!")
            return 0

        self.db_conn.commit()
        print(f"Conversation between {sender} and {receiver} sucessfully appended!")
        return 1