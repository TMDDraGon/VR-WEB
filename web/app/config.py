#configuration file for votr 
import os
from flask import Flask
from app import db

votr = Flask(__name__)


DB_PATH = os.path.join(os.path.dirname(__file__), 'votr.db')
SECRET_KEY = 'a8112ea716969327fc2a49fc8dd0e2ca9fa484033e771552' # keep this key secret during production 
SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(DB_PATH)
SQLALCHEMY_TRACK_MODIFICATIONS = False
DEBUG = True

# load config from the config file we created earlier 
votr.config.from_object('config')

# initialize and create the database 
db.init_app(votr)
db.create_all(app=votr)

@votr.route('/')
def home():
    return 'hello world'

if __name__ == '__main__':
    votr.run()