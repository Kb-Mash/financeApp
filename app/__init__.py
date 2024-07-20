from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager


app = Flask(__name__)
app.config['SECRET_KEY'] = 'SECRET_KEY'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['JWT_SECRET_KEY'] = 'JWT_SECRET_KEY'

db = SQLAlchemy(app)
bycrpt = Bcrypt(app)
jwt = JWTManager(app)
migrate = Migrate(app, db)

from app import models, routes
