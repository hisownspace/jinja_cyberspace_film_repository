from flask import Blueprint

from app.models import Genre, db

genre_routes = Blueprint("genres", __name__, url_prefix="/genres")

@genre_routes.route("/")
def get_all_genres():
  genres = Genre.query.all()
  return [[genre.id, genre.name] for genre in genres], 200