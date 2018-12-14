import os

from flask_sqlalchemy import SQLAlchemy

from . import app

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['TUXEDO_DB_URI']