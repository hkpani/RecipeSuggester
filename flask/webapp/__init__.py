from flask import Flask
from config import Config
from flask_pymongo import PyMongo

app = Flask(__name__)
#this next line sets the flask configuration based on the options set in config.py (here it is only SECRET_KEY)
#Alternatively one can just set the lines as dictionary references like "app.config['SECRET_KEY'] = blah"
app.config.from_object(Config)

#set the database location with the default Mongo localhost port 27017
app.config["MONGO_URI"] = "mongodb://localhost:27017/recipe_db"
mongo = PyMongo(app)

#avoiding circular import by importing after app has been defined
from webapp import routes