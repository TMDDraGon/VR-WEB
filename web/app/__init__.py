import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from authlib.integrations.flask_client import OAuth

app = Flask(__name__, static_folder='static')


app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'a8112ea716969327fc2a49fc8dd0e2ca9fa484033e771552'
app.config['JSON_AS_ASCII'] = False

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL", "sqlite://")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['GOOGLE_CLIENT_ID'] = os.getenv("GOOGLE_CLIENT_ID", None)
app.config['GOOGLE_CLIENT_SECRET'] = os.getenv("GOOGLE_CLIENT_SECRET", None)
app.config['GOOGLE_DISCOVERY_URL'] = os.getenv("GOOGLE_DISCOVERY_URL", None)

app.config['PATH_VIDEO'] = os.getenv("PATH_VIDEO", None)
app.config['PATH_IMG'] = os.getenv("PATH_IMG", None)
app.config['PATH_FILE'] = os.getenv("PATH_FILE", None)
app.config['PATH_IMG_WEB'] = os.getenv("PATH_IMG_WEB", None)

app.config['GMAIL_USERNAME'] = os.getenv("GMAIL_USERNAME", None)
app.config['GMAIL_PASSWORD'] = os.getenv("GMAIL_PASSWORD", None)

app.config['API_KEY_VIDEO'] = os.getenv("API_KEY_VIDEO", None)
app.config['API_KEY_SCORE'] = os.getenv("API_KEY_SCORE", None)
app.config['API_KEY_LOGIN'] = os.getenv("API_KEY_LOGIN", None)


db = SQLAlchemy(app)
oauth = OAuth(app)


login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)


from app import views  # noqa
