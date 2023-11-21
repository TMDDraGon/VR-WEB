from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin
from app import db
from .score import playing
from app.models.simulator import driver_simulator
             
class AuthUser(db.Model, UserMixin):
    __tablename__ = "players"
    email = db.Column(db.String(100), unique=True, primary_key=True)
    password = db.Column(db.String(1000))
    avatar = db.Column(db.String(1000))
    check = db.Column(db.Boolean)
    fname = db.Column(db.String(50))
    lname = db.Column(db.String(50))
    username = db.Column(db.String(50))
    bio = db.Column(db.String(300))
    phone = db.Column(db.String(20))
    gender = db.Column(db.String(10))
    location = db.Column(db.String(50))
    birthday = db.Column(db.Date)
    personality = db.Column(db.String(50))
    path = db.Column(db.String(1000))

    def __init__(self, username, email, fname, lname, password, avatar, check, phone, gender, birthday,path):
        self.username = username
        self.email = email
        self.fname = fname
        self.lname = lname
        self.password = password
        self.avatar = avatar
        self.check = check
        self.phone = phone
        self.gender = gender
        self.birthday = birthday
        self.bio = ""
        self.location = ""
        self.path = path

    def get_id(self):
        return self.email
        
    def update_password(self, password):
        self.password = password

    def update_personality(self, personality):
        self.personality = personality

class Privatescore(playing, UserMixin, SerializerMixin):
    owner_email = db.Column(db.String(100), db.ForeignKey('players.email'))
    name_state = db.Column(db.String(1000), db.ForeignKey('driver_simulator.name_state'))

    def __init__(self, owner_email, name_state, video1, video2, json, time, distance, score, speed, overturn, carbreak, crash_car, crash_platform, pass_roundabout, pass_crosswalk, zonelimit):
        super().__init__(video1, video2, json, time, distance, score, speed, overturn, carbreak, crash_car, crash_platform, pass_roundabout, pass_crosswalk, zonelimit)
        self.owner_email = owner_email
        self.name_state = name_state