DROP TABLE IF EXISTS watchlist;
CREATE TABLE watchlist (
    tmdb_id INTEGER PRIMARY KEY,
    poster TEXT NOT NULL,
    year INTEGER NOT NULL,
    rating REAL NOT NULL,
    title TEXT NOT NULL
);

INSERT INTO watchlist (tmdb_id, poster, year, rating, title) VALUES
(77, 'https://image.tmdb.org/t/p/w500/dbkEpzotHJfotpSUSYI36aPC1WN.jpg', 2000, 82, 'Memento'),
(2253, 'https://image.tmdb.org/t/p/w500/OxtxltJK6N2aNMb6x4shSdiFwY.jpg', 2008, 69, 'Walkyrie'),
(274870, 'https://image.tmdb.org/t/p/w500/o42I8c12vtqDBg9oqrUK7dzfH4e.jpg', 2016, 70, 'Passengers');

delete from movies where tmdb_id in (458156, 54111);