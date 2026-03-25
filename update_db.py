import sqlite3

connection = sqlite3.connect('database.db')

cur = connection.cursor()

cur.execute('''
    ALTER TABLE movies
    drop column tmdb_link;
''')

connection.commit()
connection.close()