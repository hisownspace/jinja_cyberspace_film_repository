from flask import render_template, redirect, request, Blueprint
from ..models import Actor, Film

search_routes = Blueprint("search", __name__, url_prefix="/search")

@search_routes.route("", methods=["GET", "POST"])
def search():
  
  query = request.args.get("query")
  
  print(query)
  actor = Actor.query.filter(Actor.name.ilike(query)).first()
  if actor:
    return redirect(f"/actors/{actor.id}")
  
  film = Film.query.filter(Film.title.ilike(query)).first()
  if film:
    return redirect(f"/films/{film.id}")
  
  else:
    return render_template("no_search_results.html", query=query)