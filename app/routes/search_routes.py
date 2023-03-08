from flask import render_template, redirect, request, Blueprint
from ..models import Actor, Film

search_routes = Blueprint("search", __name__, url_prefix="/search")

@search_routes.route("", methods=["GET", "POST"])
def search():
  
  query = request.args.get("query")
  
  actor = Actor.query.filter(Actor.name.ilike(query)).first()
  if actor:
    return redirect(f"/actors/{actor.id}")
  
  film = Film.query.filter(Film.title.ilike(query)).first()
  if film:
    return redirect(f"/films/{film.id}")
  
  else:
    actors = Actor.query.all()
    films = Film.query.all()
    film_queries = {}
    actor_queries = {}
    for actor in actors:
      check = check_search(query, actor.name.lower(), actor.id)
      if check:
        actor_queries[actor.id] = actor.name
    for film in films:
      check = check_search(query, film.title.lower(), film.id)
      if check:
        film_queries[film.id] = film.title
    return render_template("no_search_results.html", query=query, actor_queries=actor_queries, film_queries=film_queries)
  
  
def check_search(query, name, id):
    if query[:5] == name[:5]:
      return True
    count = 0
    query_copy = query
    for char in name:
      if char in query_copy:
        count += 1
        idx = query_copy.find(char)
        query_copy = query_copy[:idx] + (query_copy[idx+1:] if idx < len(query_copy) else "")
    if count / len(name) > .90 and abs(len(query)-len(name)) < 5 :
      return True
    start = 0
    matches = 0
    while start + 4 <= len(query):
      if query[start:start+4] in name:
        matches += 1
      start += 1
    if matches >= 3:
      return True
    return False