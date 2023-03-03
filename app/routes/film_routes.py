import json
from flask import Blueprint, render_template

from app.models import db, Film, Actor, Genre
from app.forms.FilmForm import FilmForm

film_routes = Blueprint("films", __name__, url_prefix="/films") 

@film_routes.route("/")
def all_films():
  films = Film.query.all()
  return { film.id: film.to_dict() for film in films }, 200

@film_routes.route("/<int:id>")
def one_film(id):
  film = Film.query.get(id)
  if not film:
    return { "errors": "Film not found" }, 404
  return film.to_dict(), 200

@film_routes.route("/count")
def film_count():
  return { "totalFilms": Film.query.count() }, 200

@film_routes.route("/add", methods=["GET", "POST"])
def add_film():
  form = FilmForm()
  

  form.genre.choices = [(genre.id, genre.name) for genre in Genre.query.all()]
  form.castIds.choices = [(actor.id, actor.name) for actor in Actor.query.all()]
  
  if form.validate_on_submit():
    print(form.data["castIds"])
    params = {
      "title": form.data["title"],
      "year": form.data["year"],
      "plot": form.data["plot"],
      "photo_url": form.data["photo_url"],
      "genre_id": form.data["genre"]
    }
    film = Film(**params)
    
    # dealing with db.relationship by appending to cast list
    cast = form.data["castIds"]
    for id in cast:
      actor = Actor.query.get(id)
      film.cast.append(actor)
    
    try:
      db.session.add(film)
      db.session.commit()
      return "Submitted!"
    except Exception as e:
      return "Unknown error!"
  if form.errors:
    print(form.errors)
  return render_template("add_film.html", form=form)
    
@film_routes.route("/<int:id>", methods=["PUT"])
def edit_film(id):
  form = FilmForm()

  form["csrf_token"].data = request.cookies["csrf_token"]

  if form.validate_on_submit():
    film = Film.query.get(id)

    film.title = form.data["title"]
    film.year = form.data["year"]
    film.plot = form.data["plot"]
    film.photo_url = form.data["photo_url"]
    film.genre_id = form.data["genre_id"]

    # dealing with db.relationship by appending to new list, and replacing old
    # cast relationship list with new list
    castIds = json.loads(form.data["castIds"])
    cast = []
    for actor_id in castIds:
      actor = Actor.query.get(actor_id)
      cast.append(actor)
    film.cast = cast
    
    try:
      db.session.add(film)
      db.session.commit()
      return film.to_dict(), 200
    except Exception as e:
      return { "errors": str(e) }, 500
  
  return { "errors": form.errors }, 400


@film_routes.route("/<int:id>", methods=["DELETE"])
def delete_film(id):
  film = Film.query.get(id)
  if film:
    try:
      db.session.delete(film)
      db.session.commit()
      return { "message": f"Successfully deleted {film.title}!" }, 204
    except Exception as e:
      return { "errors": str(e) }, 500
  return { "errors": "Actor not found!" }, 404

# @film_routes("/<int:id>", methods=["PUT"])
# def update_film(id):
#   form = FilmForm()
#   form["csrf_token"].data = request.cookies["csrf_token"]
#   if form.validate_on_submit():
#     film = Film.query.get(id)

#     film.title = form.data["title"]
#     film.year = form.data["year"]
#     film.plot = form.data["plot"]
#     film.photo_url = form.data["photo_url"]
#     film.genre_id = form.data["genre_id"]
    
    