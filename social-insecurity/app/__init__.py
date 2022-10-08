from flask import Flask, g, session
from config import Config
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, UserMixin
import sqlite3
import os
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
Bootstrap(app)
app.config.from_object(Config)

app.config.update(
    SESSION_COOKIE_SAMESITE='Strict',
    SESSION_COOKIE_SECURE='True'
)

login_manager = LoginManager(app)
login_manager.login_view = 'index'

db = SQLAlchemy(app)


@app.after_request
def set_secure_headers(response):
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    return response


class User(UserMixin):
    def __init__(self,id,username):
        self.id=id
        self.username=username


@login_manager.user_loader
def load_user(user_id):
    user = query_db('SELECT * FROM Users WHERE id="{}";'.format(user_id), one=True)
    if user is None:
        return None
    else:
        return User(user_id,user[1])



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
