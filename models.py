import os
from sqlalchemy import Column, String, Integer
from flask_sqlalchemy import SQLAlchemy
import json

'''
database_name = "casting_agency"
database_path = f"postgresql://omar@:5432/{database_name}"
'''
database_url = os.environ.get('DATABASE_URL')

db = SQLAlchemy()
def setup_db(app, database_path=database_path):

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)





helper_table = db.Table('helper',
    db.Column('movie_id', db.Integer, db.ForeignKey('Movie.id'), primary_key=True),
    db.Column('actor_id', db.Integer, db.ForeignKey('Actor.id'), primary_key=True)
)


class Actor(db.Model):
    __tablename__ = 'Actor'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True , nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.Enum('m','f', name='gender_types'), nullable=False)

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def format(self):
        return f"{self.name} - {self.age} - {self.gender}"


class Movie(db.Model):
    __tablename__ = 'Movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), unique=True, nullable=False)
    release_date = db.Column(db.Date(), nullable=False)
    actors = db.relationship('Actor', secondary=helper_table, backref=db.backref('movies', lazy=True))

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def format(self):
        return f"{self.title} - {self.release_date}"







'''
def db_drop_and_create_all():
    db.drop_all()
    db.create_all()
'''
