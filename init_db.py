import sqlite3

connection = sqlite3.connect('database.db')

cur = connection.cursor()

cur.execute('''
    drop table if exists movies;
''')
cur.execute('''
    drop table if exists genres;
''')

cur.execute('''
    create table movies(
        title text,
        poster text,
        tmdb_id integer primary key,
        rating integer,
        date text,
        year integer,
        summary text,
        review text,
        director text,
        runtime text,
        average_rating real,
        banner text
    );
''')

cur.execute('''
    create table genres(
        tmdb_id integer,
        genre text,
        primary key(tmdb_id, genre),
        FOREIGN KEY (tmdb_id) REFERENCES movies(tmdb_id)
    );
''')

connection.commit()
connection.close()