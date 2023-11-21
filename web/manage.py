from flask.cli import FlaskGroup
from werkzeug.security import generate_password_hash
from app import app, db
from app.models.authuser import AuthUser
from app.models.simulator import driver_simulator

cli = FlaskGroup(app)

@cli.command("create_db")
def create_db():
    db.drop_all()
    db.create_all()
    db.session.commit()

@cli.command("seed_db")
def seed_db():
    db.session.add(AuthUser(email="vokox44702@utwoko.com",username='tripleS', fname='mai',lname='mai',
                            password=generate_password_hash('1234', method='scrypt'),
                            avatar='avatar_bf5873336c105eb30b804ce9b894cfaa.jpg', 
                            check=False, phone="", gender="", birthday=None,path='sha256$RHKzYoKwVAqOS8gR$060b11b330dab82c7c4a4d0d9b8cb47c50f8169047038431e0430b98d2b14bf4'))
    db.session.add(AuthUser(email="teeranai_c@cmu.ac.th",username='Dragon', fname='Teeranai',lname='chai',
                            password=generate_password_hash('1234', method='scrypt'),
                            avatar='avatar_bf5873336c105eb30b804ce9b894cfaa.jpg', 
                            check=False, phone="", gender="", birthday=None,path='sha257$RHKzYoKwVAqOS8gR$060b11b330dab82c7c4a4d0d9b8cb47c50f8169047038431e0430b98d2b14bf4'))
    db.session.add(AuthUser(email="pachara_chai@cmu.ac.th",username='A', fname=' Pachara',lname='Chairungsi',
                            password=generate_password_hash('1234', method='scrypt'),
                            avatar='avatar_bf5873336c105eb30b804ce9b894cfaa.jpg', 
                            check=False, phone="", gender="", birthday=None,path='sha258$RHKzYoKwVAqOS8gR$060b11b330dab82c7c4a4d0d9b8cb47c50f8169047038431e0430b98d2b14bf4'))
    
    db.session.add(driver_simulator(name_state="roundabout_test_simple", car_roundabout=10,car_inroad=0,
                            time='day', weather="no", lane_check=False))
    db.session.add(driver_simulator(name_state="roundabout_test_middle", car_roundabout=10,car_inroad=2,
                            time='day', weather="rain", lane_check=False))
    db.session.commit()

if __name__ == "__main__":
    cli()