from app.extensions import db

class Movie(db.Model):
    __tablename__ = "movies"
    tmdb_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    poster = db.Column(db.Text)
    rating = db.Column(db.Integer)
    date = db.Column(db.Text)
    year = db.Column(db.Integer)
    summary = db.Column(db.Text)
    review = db.Column(db.Text)
    director = db.Column(db.Text)
    runtime = db.Column(db.Text)
    average_rating = db.Column(db.Float)
    banner = db.Column(db.Text)

    genres = db.relationship("Genre", backref="movie", cascade="all, delete-orphan", lazy=True)

    __table_args__ = (
        db.Index("idx_movies_date", "date"),
        db.Index("idx_movies_title", "title"),
        db.CheckConstraint("rating IS NULL OR (rating >= 0 AND rating <= 100)", name="ck_movies_rating"),
        db.CheckConstraint("year IS NULL OR (year >= 1888 AND year <= 2100)", name="ck_movies_year"),
        db.CheckConstraint(
            "average_rating IS NULL OR (average_rating >= 0 AND average_rating <= 100)",
            name="ck_movies_avg_rating",
        ),
    )

    def __repr__(self):
        return f"<Movie {self.tmdb_id}:{self.title}>"

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Genre(db.Model):
    __tablename__ = "genres"
    tmdb_id = db.Column(db.Integer, db.ForeignKey("movies.tmdb_id", ondelete="CASCADE"), primary_key=True)
    genre = db.Column(db.Text, primary_key=True)

    def __repr__(self):
        return f"<Genre {self.tmdb_id}:{self.genre}>"


class Watchlist(db.Model):
    __tablename__ = "watchlist"
    tmdb_id = db.Column(db.Integer, primary_key=True)
    poster = db.Column(db.Text, nullable=False)
    year = db.Column(db.Integer)
    rating = db.Column(db.Float, nullable=False)
    title = db.Column(db.Text, nullable=False)

    __table_args__ = (
        db.CheckConstraint("rating >= 0 AND rating <= 100", name="ck_watchlist_rating"),
        db.CheckConstraint("year IS NULL OR (year >= 1888 AND year <= 2100)", name="ck_watchlist_year"),
    )

    def __repr__(self):
        return f"<Watchlist {self.tmdb_id}:{self.title}>"

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
