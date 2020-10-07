import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from app import *
from models import setup_db, Actor , Movie



class CapstoneTestCase(unittest.TestCase):

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "casting_agency_test"
        self.database_path = f"postgresql://omar@:5432/{self.database_name}"
        setup_db(self.app, self.database_path)

        self.new_actor = {
        "name": "Dwayne Johnson",
        "age": 50,
        "gender": "m"
        }

        self.new_movie = {
        "title": "Inception",
        "release_date": "2010-06-25"
        }


        # tokens can be generated using /login endpoint and signing in with the info
        self.casting_assistant = os.environ.get('ASSISTANT')
        self.casting_director = os.environ.get('DIRECTOR')
        self.executive_producer = os.environ.get('PRODUCER')
        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass



    ## Actor tests
    ########################################################################
    def test_add_actor(self):
        res = self.client().post('/actors',headers={"Authorization": "Bearer {}".format(self.casting_director)},
                                                json= {"name": "John Doe","age": 27,"gender": "m"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['actors'])
        self.assertTrue(len(data['actors']))


    def test_400_no_inputs_for_add_actor(self):
        res = self.client().post('/actors',headers={"Authorization": "Bearer {}".format(self.casting_director)})

        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'bad request')



    def test_delete_actor(self):
        insertion_response = self.client().post('/actors', headers={"Authorization": "Bearer {}".format(self.casting_director)},
                                                json= self.new_actor)
        insertion_data = json.loads(insertion_response.data)
        actor_id = insertion_data['created_id']

        res = self.client().delete(f'/actors/{actor_id}', headers={"Authorization": "Bearer {}".format(self.casting_director)})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], actor_id)


    def test_422_delete_actor_failure(self):
        res = self.client().delete('/actors/1000', headers={"Authorization": "Bearer {}".format(self.casting_director)})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')


    def test_get_actor(self):
        res = self.client().get('/actors/1', headers={"Authorization": "Bearer {}".format(self.casting_assistant)})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['name'])


    def test_404_get_actor_failure(self):
        res = self.client().get('/actors/1000', headers={"Authorization": "Bearer {}".format(self.casting_assistant)})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')


    def test_get_all_actors(self):
        res = self.client().get('/actors', headers={"Authorization": "Bearer {}".format(self.casting_assistant)})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['actors'])


    def test_404_get_all_actors_failure(self): # no actors found
        res = self.client().get('/actors', headers={"Authorization": "Bearer {}".format(self.casting_assistant)})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')


    def test_404_update_actor_failure(self): # no actor found with the given id
        res = self.client().patch('/actors/1000', headers={"Authorization": "Bearer {}".format(self.casting_director)},json = self.new_actor)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')


    def test_400_update_actor_failure(self): # no inputs is given for actor
        res = self.client().patch('/actors/1', headers={"Authorization": "Bearer {}".format(self.casting_director)})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'bad request')


    ## Movie tests
    ########################################################################
    def test_add_movie(self):
        res = self.client().post('/movies', headers={"Authorization": "Bearer {}".format(self.executive_producer)},
                                                json= {"title": "Ghost Busters","release_date": "2015-07-12"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['movies'])
        self.assertTrue(len(data['movies']))


    def test_400_no_inputs_for_add_movie(self):
        res = self.client().post('/movies', headers={"Authorization": "Bearer {}".format(self.executive_producer)})

        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'bad request')



    def test_delete_movie(self):
        insertion_response = self.client().post('/movies', headers={"Authorization": "Bearer {}".format(self.executive_producer)},
                                                    json= self.new_movie)
        insertion_data = json.loads(insertion_response.data)
        movie_id = insertion_data['created_id']

        res = self.client().delete(f'/movies/{movie_id}', headers={"Authorization": "Bearer {}".format(self.executive_producer)})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], movie_id)


    def test_422_delete_movie_failure(self):
        res = self.client().delete('/movies/1000', headers={"Authorization": "Bearer {}".format(self.executive_producer)})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')


    def test_get_movie(self):
        res = self.client().get('/movies/1', headers={"Authorization": "Bearer {}".format(self.casting_assistant)})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['title'])


    def test_404_get_movie_failure(self):
        res = self.client().get('/movies/1000', headers={"Authorization": "Bearer {}".format(self.casting_assistant)})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')


    def test_get_all_movies(self):
        res = self.client().get('/movies', headers={"Authorization": "Bearer {}".format(self.casting_assistant)})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['movies'])


    def test_404_get_all_movies_failure(self): # no movies found
        res = self.client().get('/movies', headers={"Authorization": "Bearer {}".format(self.casting_assistant)})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')


    def test_404_update_movie_failure(self): # no movie found with the given id
        res = self.client().patch('/movies/1000', headers={"Authorization": "Bearer {}".format(self.casting_director)},
                                    json = self.new_movie)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')


    def test_400_update_movie_failure(self): # no inputs is given for movie
        res = self.client().patch('/movies/1', headers={"Authorization": "Bearer {}".format(self.casting_director)})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'bad request')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
