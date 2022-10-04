import os

# contains application-wide configuration, and is loaded in __init__.py

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'secret' 
    DATABASE = 'database.db'
    UPLOAD_PATH = 'app/static/uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}