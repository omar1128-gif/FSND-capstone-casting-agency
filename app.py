import os
import secrets
from flask import Flask, request, abort, jsonify , render_template, session , url_for , redirect
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
from authlib.integrations.flask_client import OAuth
from six.moves.urllib.parse import urlencode
from datetime import datetime

from models import db, setup_db, Actor, Movie
from auth.auth import *



def create_app(test_config=None):
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    oauth = OAuth(app)

    secret = secrets.token_urlsafe(32)
    app.secret_key = secret
    auth0 = oauth.register(
        'auth0',
        client_id= os.environ.get('CLIENT_ID'),
        client_secret=os.environ.get('CLIENT_SECRET'),
        api_base_url=os.environ.get('API_BASE_URL'),
        access_token_url=os.environ.get('ACCESS_TOKEN_URL'),
        authorize_url=os.environ.get('AUTHORIZE_URL'),
        client_kwargs={
            'scope': 'openid profile email',
        },
    )
    AUTH0_URL = os.environ.get('AUTH0_LOGIN_URL')

    CORS(app, resources={r"/api/*": {"origins": "*"}})




    ## ROUTES


    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response


    # main page
    @app.route('/')
    def index():
        return 'Hello, friend !'

    # login page
    @app.route('/login')
    def login():
        return render_template('login.html',AUTH0_AUTHORIZE_URL=AUTH0_URL)


    # logout
    @app.route('/logout')
    def logout():
        # Clear session stored data
        session.clear()
        # Redirect user to logout endpoint
        params = {'returnTo': url_for('index', _external=True), 'client_id': '5FmE550Gvrv7iLRl1WxYleKWZx44su3a'}
        return redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))




    ## GET endpoints
    ##################################################################


    # retrieves all the actors
    @app.route('/actors', methods=['GET'])
    @requires_auth('get:actors')
    def show_actors(jwt):
        actors = Actor.query.all()
        if actors is None:
            abort(404)

        actors_list = []
        for actor in actors:
            actors_list.append({
            'actor_id': actor.id,
            'actor_name': actor.name,
            'actor_age': actor.age,
            'actor_gender': actor.gender
            })


        return jsonify({
        'success': True,
        'actors': actors_list
        })


    # retrieves all the movies
    @app.route('/movies', methods= ['GET'])
    @requires_auth('get:movies')
    def show_movies(jwt):
        movies = Movie.query.all()
        if movies is None:
            abort(404)

        movies_list = []
        for movie in movies:
            movies_list.append({
            'movie_id': movie.id,
            'movie_title': movie.title,
            'movie_release_date': movie.release_date
            })

        return jsonify({
        'success': True,
        'movies': movies_list
        })


    # retrieves a certain actor
    @app.route('/actors/<int:actor_id>',methods=['GET'])
    @requires_auth('get:actor')
    def show_actor(jwt, actor_id):
        actor = Actor.query.filter(Actor.id == actor_id).one_or_none()
        if actor is None:
            abort(404)

        return jsonify({
        'success': True,
        'name': actor.name,
        'age': actor.age,
        'gender': actor.gender
        })


    # retrieves a certain movie
    @app.route('/movies/<int:movie_id>', methods=['GET'])
    @requires_auth('get:movie')
    def show_movie(jwt, movie_id):
        movie = Movie.query.filter(Movie.id == movie_id).one_or_none()
        if movie is None:
            abort(404)

        return jsonify({
        'success': True,
        'title': movie.title,
        'release_date': movie.release_date
        })


    ## Delete endpoints
    ##################################################################

    # deletes a certain actor
    @app.route('/actors/<int:actor_id>', methods=['DELETE'])
    @requires_auth('delete:actor')
    def delete_actor(jwt, actor_id):
        try:
            actor = Actor.query.filter(Actor.id == actor_id).one_or_none()

            if actor is None:
                abort(404)

            actor.delete()

            return jsonify({
            "success": True,
            "deleted": actor_id
            })
        except:
            abort(422)


    # retrieves a certain movie
    @app.route('/movies/<int:movie_id>', methods=['DELETE'])
    @requires_auth('delete:movie')
    def delete_movie(jwt, movie_id):
        try:
            movie = Movie.query.filter(Movie.id == movie_id).one_or_none()

            if movie is None:
                abort(404)

            movie.delete()

            return jsonify({
            "success": True,
            "deleted": movie_id
            })
        except:
            abort(422)


    ## POST endpoints
    ##################################################################

    # adds a new actor
    @app.route('/actors', methods=['POST'])
    @requires_auth('post:actor')
    def add_actor(jwt):
        body = request.get_json()
        if body is None:
            abort(400)

        new_name = body.get('name', None)
        new_age = body.get('age', None)
        new_gender = body.get('gender', None)
        try:
            if new_name and new_age and new_gender :
                new_actor = Actor(
                name = new_name,
                age = new_age,
                gender = new_gender
                )
                new_actor.insert()
                return jsonify({
                'success': True,
                'created_id': new_actor.id,
                'actors': [actor.format() for actor in Actor.query.all()]
                })

            else:
                abort(422)
        except:
            abort(422)


    # adds a new movie
    @app.route('/movies', methods=['POST'])
    @requires_auth('post:movie')
    def add_movie(jwt):
        body = request.get_json()
        if body is None:
            abort(400)

        new_title = body.get('title', None)
        release_date_str = body.get('release_date', None)
        y, m , d = release_date_str.split('-')
        new_release_date = datetime(int(y), int(m), int(d)).date()
        try:
            if new_title and release_date_str:
                new_movie = Movie(title=new_title, release_date= new_release_date)

                new_movie.insert()
                return jsonify({
                'success': True,
                'created_id': new_movie.id,
                'movies': [movie.format() for movie in Movie.query.all()]
                })

            else:
                abort(422)
        except:
            abort(422)


    ## PATCH endpoints
    ##################################################################
    # updates an existing actor
    @app.route('/actors/<int:actor_id>', methods=['PATCH'])
    @requires_auth('patch:actor')
    def update_actor(jwt, actor_id):

        actor = Actor.query.filter(Actor.id == actor_id).one_or_none()
        if actor is None:
            abort(404)

        body = request.get_json()
        if body is None:
            abort(400)

        new_name = body.get('name', None)
        new_age = body.get('age', None)
        new_gender = body.get('gender', None)
        try:
            if new_name:
                actor.name = new_name

            if new_age:
                actor.age = new_age

            if new_gender:
                actor.gender = new_gender

            actor.update()

            return jsonify({
            "success": True,
            "actor": [actor.format() for actor in Actor.query.all()]
            })
        except:
            abort(422)


    # updates an existing movie
    @app.route('/movies/<int:movie_id>', methods=['PATCH'])
    @requires_auth('patch:movie')
    def update_movie(jwt, movie_id):

        movie = Movie.query.filter(Movie.id == movie_id).one_or_none()
        if movie is None:
            abort(404)

        body = request.get_json()
        if body is None:
            abort(400)

        new_title = body.get('title', None)
        new_release_date_str = body.get('release_date', None)

        try:
            if new_title:
                movie.title = new_title

            if new_release_date_str:
                y, m , d = new_release_date_str.split('-')
                new_release_date = datetime(int(y), int(m), int(d)).date()
                movie.release_date = new_release_date

            movie.update()

            return jsonify({
            "success": True,
            "movies": [movie.format() for movie in Movie.query.all()]
            })
        except:
            abort(422)



    ## Error Handling

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
                        "success": False,
                        "error": 422,
                        "message": "unprocessable"
                        }), 422

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
                        "success": False,
                        "error": 404,
                        "message": "resource not found"
                        }), 404


    @app.errorhandler(AuthError)
    def authentication_error(error):
        return jsonify({
                        "success": False,
                        "error": 401,
                        "message": "AuthError"
                        }), 401



    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
                        "success": False,
                        "error": 400,
                        "message": 'bad request'
                        }), 400

    return app

app = create_app()

if __name__ == '__main__':
    APP.run(host='0.0.0.0', port=8080, debug=True)
