import sqlite3
import os

BASE_DIR = os.path.dirname(__file__)
connection = sqlite3.connect(os.path.join(BASE_DIR, 'database.db'))

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

cur.execute('''
CREATE TABLE watchlist (
    tmdb_id INTEGER PRIMARY KEY,
    poster TEXT NOT NULL,
    year INTEGER NOT NULL,
    rating REAL NOT NULL,
    title TEXT NOT NULL
);
''')


connection.commit()
connection.close()