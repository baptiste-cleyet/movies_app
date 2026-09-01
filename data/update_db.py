import sqlite3

connection = sqlite3.connect('data/database.db')

cur = connection.cursor()

with open('data/update.sql', 'r') as f:
    sql_script = f.read()
    cur.executescript(sql_script)

connection.commit()
connection.close()