from sqlalchemy_serializer import SerializerMixin
from app import db

class driver_simulator(db.Model, SerializerMixin):
    __tablename__ = "driver_simulator"
    name_state = db.Column(db.String(1000), unique=True, primary_key=True)
    car_roundabout = db.Column(db.Integer)
    car_inroad = db.Column(db.Integer)
    weather = db.Column(db.String(100))
    time = db.Column(db.String(100))
    lane_check = db.Column(db.Boolean)
    
    def __init__(self, name_state, car_roundabout, car_inroad, time, weather, lane_check):
        self.name_state = name_state
        self.car_roundabout=car_roundabout
        self.car_inroad=car_inroad
        self.weather=weather
        self.time=time
        self.lane_check=lane_check