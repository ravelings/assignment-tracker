import sqlite3 

connection = sqlite3.connect('login.db')

cursor = connection.cursor() 

command = """ALTER TABLE login ADD COLUMN id"""

cursor.execute(command)
cursor.execute()
print(cursor.fetchall())