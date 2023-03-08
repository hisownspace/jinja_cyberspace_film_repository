from flask import Blueprint, request, render_template, redirect
from datetime import date

from app.models import db, Actor, Film

from app.forms.ActorForm import ActorForm

actor_routes = Blueprint("actors", __name__, url_prefix="/actors")

@actor_routes.route("/", methods=["GET", "POST"])
def all_actors():
  """"""
  form = ActorForm()
  form["csrf_token"].data = request.cookies["csrf_token"]

  if form.validate_on_submit():

    # dealing with db.relationship on filmography by finding
    # films that correspond with the ids in the list received
    # in the form and appending each Film instance to filmography
    # relationship on the Actor instance
    film_ids = form.data["filmography"]
    filmography = [Film.query.get(id) for id in film_ids]
    
    params = {
      "name": form.data["name"],
      "date_of_birth": form.data["date_of_birth"],
      "place_of_birth": form.data["place_of_birth"],
      "photo_url": form.data["photo_url"],
      "bio": form.data["bio"],
      "filmography": filmography
    }
    actor = Actor(**params)

    db.session.add(actor)
    db.session.commit()

    return actor.to_dict(), 201, { "Content-Type": "application/json" }
  
  elif form.errors:
    return { "errors": form.errors }, 400, { "Content-Type": "application/json" }
  else:
    actors = Actor.query.all()
    return { actor.id: actor.to_dict() for actor in actors }, 200, { "Content-Type": "application/json" }

@actor_routes.route("/<int:id>") 
def one_actor(id):
  actor = Actor.query.get(id)
  if actor:
    return render_template("single_actor.html", actor=actor.to_dict())
  return { "errors": "Actor not found!" }, 404, { "Content-Type": "application/json" }
  
@actor_routes.route("/count")
def actor_count():
  return { "totalActors": Actor.query.count() }, 200, { "Content-Type": "application/json" }

@actor_routes.route("/add", methods=["GET", "POST"])
def add_actor():
  form = ActorForm()
  
  form.filmography.choices = [(film.id, film.title) for film in Film.query.all()]
  
  if form.validate_on_submit():
    params = {
      "name": form.data["name"],
      "date_of_birth": form.data["date_of_birth"],
      "place_of_birth": form.data["place_of_birth"],
      "photo_url": form.data["photo_url"],
      "bio": form.data["bio"],
      # "filmography": form.data["filmography"]
    }
    
    print(params)
    actor = Actor(**params)

    [actor.filmography.append(Film.query.get(id)) for id in form.data["filmography"]]

    try:
      db.session.add(actor)
      db.session.commit()
      return redirect(f"/actors/{actor.id}")
    except Exception as e:
      return "Unknown error!"
  if form.errors:
    print(form.errors)
  return render_template("add_actor.html", form=form)
  
@actor_routes.route("/<int:id>/edit", methods=["GET", "POST"])
def edit_actor(id):
  form = ActorForm()
  
  form.filmography.choices = [(film.id, film.title) for film in Film.query.all()]

  actor = Actor.query.get(id)

  if form.validate_on_submit():
    actor = Actor.query.get(id)
    
    actor.name = form.data["name"]
    actor.date_of_birth = form.data["date_of_birth"]
    actor.place_of_birth = form.data["place_of_birth"]
    actor.photo_url = form.data["photo_url"]
    actor.bio = form.data["bio"]
    actor.filmography = []
    [actor.filmography.append(Film.query.get(id)) for id in form.data["filmography"]]

    db.session.commit()
    return redirect(f"/actors/{actor.id}")

  elif form.errors:
    return render_template("edit_actor.html", form=form, id=actor.id)
  else:
    form.name.data = actor.name
    form.date_of_birth.data = actor.date_of_birth
    form.place_of_birth.data = actor.place_of_birth
    form.photo_url.data = actor.photo_url
    form.bio.data = actor.bio
    form.filmography.data = [film.id for film in actor.filmography]
    
    return render_template("edit_actor.html", form=form, id=actor.id)

@actor_routes.route("/<int:id>/delete")
def get_delete(id):
  return delete_actor(id)

@actor_routes.route("/<int:id>", methods=["DELETE"])
def delete_actor(id):
  actor = Actor.query.get(id)
  if actor:
    db.session.delete(actor)
    db.session.commit()
    return redirect("/")
    # return { "message": f"Successfully deleted {actor.name}!" }, 204, { "Content-Type": "application/json" }
  return { "errors": "Actor not found!" }, 404, { "Content-Type": "application/json" }

@actor_routes.route("/<int:id>", methods=["PUT"])
def update_actor(id):
  form = ActorForm()
  form["csrf_token"].data = request.cookies["csrf_token"]
  if form.validate_on_submit():
    actor = Actor.query.get(id)

    # dealing with db.relationship by creating new list, adding
    # all the values from the list in the form, and replacing
    # the actor.films relationship list with new list
    films = []
    for film_id in form.data["filmography"]:
      film = Film.query.get(film_id)
      films.append(film)

    actor.name = form.data["name"]
    actor.date_of_birth = form.data["date_of_birth"]
    actor.place_of_birth = form.data["place_of_birth"]
    actor.photo_url = form.data["photo_url"]
    actor.bio = form.data["bio"]
    actor.filmography = films

    try:
      db.session.add(actor)
      db.session.commit()
    except Exception as e:
      return { "errors": str(e) }, 500

    return actor.to_dict(), 200, { "Content-Type": "application/json" }
  return { "errors": form.errors }, 400, { "Content-Type": "application/json" }
