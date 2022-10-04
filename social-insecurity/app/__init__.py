from flask import Flask, g
from config import Config
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
import sqlite3
import os

login_manager = LoginManager()

# create and configure app
app = Flask(__name__)
Bootstrap(app)
app.config.from_object(Config)


# TODO: Handle login management better, maybe with flask_login?
login = LoginManager(app)

from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    """An admin user capable of viewing reports.
    :param str email: email address of user
    :param str password: encrypted password for the user
    """
    __tablename__ = 'users'

    email = db.Column(db.String, primary_key=True)
    password = db.Column(db.String)
    authenticated = db.Column(db.Boolean, default=False)

    def is_active(self):
        """True, as all users are active."""
        return True

    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        return self.email

    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return self.authenticated

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False

# get an instance of the db
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
    db.row_factory = sqlite3.Row
    return db

# initialize db for the first time
def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

# perform generic query, not very secure yet
def query_db(query, one=False):
    db = get_db()
    cursor = db.execute(query)
    rv = cursor.fetchall()
    cursor.close()
    db.commit()
    return (rv[0] if rv else None) if one else rv

# TODO: Add more specific queries to simplify code

# automatically called when application is closed, and closes db connection
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# initialize db if it does not exist
if not os.path.exists(app.config['DATABASE']):
    init_db()

if not os.path.exists(app.config['UPLOAD_PATH']):
    os.mkdir(app.config['UPLOAD_PATH'])

from app import routes