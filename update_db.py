import sqlite3

connection = sqlite3.connect('database.db')

cur = connection.cursor()

cur.execute('''
    # Write you SQL statement here.
''')

connection.commit()
connection.close()