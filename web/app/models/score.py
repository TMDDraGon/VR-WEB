from sqlalchemy import ARRAY
from sqlalchemy_serializer import SerializerMixin
from app import db
from datetime import datetime
import uuid

class playing(db.Model, SerializerMixin):
    __tablename__ = "playing"
    id = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()), unique=True)
    time = db.Column(db.Integer)
    distance = db.Column(db.Integer)
    score = db.Column(db.Integer)
    speed = db.Column(db.Float)
    overturn = db.Column(db.Integer)
    carbreak = db.Column(db.Integer)
    crash_car = db.Column(db.Integer)
    crash_platform = db.Column(db.Integer)
    pass_roundabout = db.Column(ARRAY(db.Integer))
    pass_crosswalk = db.Column(ARRAY(db.Integer))
    zonelimit = db.Column(ARRAY(db.Integer))
    datetime = db.Column(db.DateTime)
    video1 = db.Column(db.String(1000))
    video2 = db.Column(db.String(1000))
    json = db.Column(db.String(1000))

    
    def __init__(self, video1, video2, json, time, distance, score, speed, overturn, carbreak, crash_car, crash_platform, pass_roundabout, pass_crosswalk, zonelimit):
        self.id = str(uuid.uuid4())
        self.video1 = video1
        self.video2 = video2
        self.json = json
        self.time = time
        self.distance = distance
        self.score = score
        self.speed = speed
        self.overturn = overturn
        self.carbreak = carbreak
        self.crash_car = crash_car
        self.crash_platform = crash_platform
        self.pass_roundabout = pass_roundabout
        self.pass_crosswalk = pass_crosswalk 
        self.zonelimit = zonelimit   
        self.datetime = datetime.now()
