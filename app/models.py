from app.extensions import db

class Movie(db.Model):
    __tablename__ = "movies"
    tmdb_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
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
    )

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Genre(db.Model):
    __tablename__ = "genres"
    tmdb_id = db.Column(db.Integer, db.ForeignKey("movies.tmdb_id", ondelete="CASCADE"), primary_key=True)
    genre = db.Column(db.Text, primary_key=True)


class Watchlist(db.Model):
    __tablename__ = "watchlist"
    tmdb_id = db.Column(db.Integer, primary_key=True)
    poster = db.Column(db.Text, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Float, nullable=False)
    title = db.Column(db.Text, nullable=False)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
