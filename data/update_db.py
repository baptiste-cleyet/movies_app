import sqlite3
import os

BASE_DIR = os.path.dirname(__file__)
connection = sqlite3.connect(os.path.join(BASE_DIR, 'database.db'))

cur = connection.cursor()

with open(os.path.join(BASE_DIR, 'update.sql'), 'r') as f:
    sql_script = f.read()
    cur.executescript(sql_script)

connection.commit()
connection.close()