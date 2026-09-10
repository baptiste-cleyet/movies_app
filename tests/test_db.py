from app.models import Movie, Genre, Watchlist

def test_movie_crud(app, db):
    with app.app_context():
        m = Movie(tmdb_id=1, title="Test", year=2020, rating=80, poster="x", average_rating=75.0)
        db.session.add(m)
        db.session.commit()
        assert Movie.query.get(1).title == "Test"
        # genre cascade
        g = Genre(tmdb_id=1, genre="Action")
        db.session.add(g)
        db.session.commit()
        assert len(Movie.query.get(1).genres) == 1
        # delete cascade
        db.session.delete(m)
        db.session.commit()
        assert Genre.query.filter_by(tmdb_id=1).count() == 0

def test_watchlist(db, app):
    with app.app_context():
        w = Watchlist(tmdb_id=99, title="WL", poster="p", year=2021, rating=70)
        db.session.add(w)
        db.session.commit()
        assert Watchlist.query.get(99).title == "WL"
        db.session.delete(w)
        db.session.commit()
        assert Watchlist.query.get(99) is None
