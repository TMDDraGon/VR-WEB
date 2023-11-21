from ctypes import cast
from datetime import datetime
from email.mime.text import MIMEText
from functools import wraps
import os
import random
import secrets
import shutil
import smtplib
import string
import time
import uuid
from app.driving_prediction import personal_detection
from flask import (abort, jsonify, session,send_from_directory, render_template,
                   request, url_for, flash, redirect)
from sqlalchemy import asc, desc
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from app.models.authuser import AuthUser, Privatescore
from app.models.simulator import driver_simulator
from app import login_manager, app, db, oauth
from random_username.generate import generate_username
import pyotp
import smtplib
import threading
import boringavatars
import json
import pandas as pd
import re

@login_manager.user_loader
def load_user(user_id):
    return AuthUser.query.get(user_id)

@app.route('/')
def newbase():
    return render_template('newbase.html',)

@app.route('/base')
def base():
    return render_template('newbase.html')

def login_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('newbase')) 
        return func(*args, **kwargs)
    return decorated_function

@app.route('/imgweb/<filename>')
def imgweb(filename):
    folder_path = app.config['PATH_IMG_WEB']
    file_path = os.path.join(folder_path, filename)

    if os.path.exists(file_path):
        return send_from_directory(folder_path, filename)
    else:
        # Use abort to send a 404 error response.
        abort(404)

SESSION_TIMEOUT = 300  # 5 minutes (adjust as needed)

# Define a decorator function for session expiration cleanup.
@app.before_request
def session_expiration_cleanup():
    current_time = time.time()
    
    # Check the main session expiration.
    if 'session_expiration_time' in session and current_time > session['session_expiration_time']:
        session.pop('session_expiration_time', None)
        session.pop('check', None)
        session.pop('generated_otp', None)
        session.pop('OTP_KEY', None)
        session.pop('recipient_email', None)

    # Check the signup session expiration.
    if 'session_expiration_time_signup' in session and current_time > session['session_expiration_time_signup']:
        session.pop('session_expiration_time_signup', None)
        session.pop('check_signup', None)
        session.pop('generated_otp_signup', None)
        session.pop('OTP_KEY_signup', None)

P_speed = "Reduce your speed immediately."
P_car = "Focus on the road and the drivers around you."

# ----------------------------------------------------------------------profile---------------------------------------------------------------------
def my_time(id):
    # Retrieve all Privatescore objects associated with the given owner_email,
    # order them by score in descending order, and retrieve them as a list.
    all_my_score = Privatescore.query.filter_by(owner_email=id).order_by(desc('score')).all()

    # Initialize a variable to store the total time.
    total_time = 0 

    # Iterate through all Privatescore objects and sum up their time.
    for my in all_my_score:
        total_time += my.time

    # Calculate hours, minutes, and seconds from the total time.
    hours = total_time // 3600
    total_time %= 3600
    minutes = total_time // 60
    total_time %= 60

    # Create a time string in the format "X hrs, Y mins".
    time_str = f"{hours} hrs, {minutes} mins"

    # Return the formatted time string.
    return time_str

@app.route('/profile')
@login_required
def profile():

    # Query the highest score for the current user.
    my_score = Privatescore.query.filter_by(owner_email=current_user.email, distance=100).order_by(desc('score')).first()

    if not my_score:
        # If there is no score for the user, display default values.
        return render_template('profile.html', rank="-", time="0 mins")

    # Calculate the user's ranking based on their score.
    ranking = my_ranking(my_score.score)

    # Calculate the total time for the user.
    id = current_user.email
    time = my_time(id)

    # Render the profile template with the user's rank and time.
    return render_template('profile.html', rank=ranking, time=time)

@app.route('/profile/<email>')

def profile_user(email):
    if current_user.is_authenticated and email == current_user.email:
        # If the requested username matches the current user, redirect to the user's own profile.
        return redirect(url_for('profile'))
    else:
        # Retrieve the user by their username.
        user = AuthUser.query.filter_by(email=email).first()
        
        if not user:
            # If the user does not exist, return a 404 error.
            abort(404)
        
        # Query the highest score for the user.
        my_score = Privatescore.query.filter_by(owner_email=email, distance=100).order_by(desc('score')).first()
        
        if not my_score:
            # If there is no score for the user, set ranking to 0 and time to "0 mins."
            ranking = "-"
            time = "0 mins"
        else:
            # Calculate the user's ranking based on their score.
            ranking = my_ranking(my_score.score)
            
            # Calculate the total time for the user.
            time = my_time(user.email)
        
        # Prepare user data for rendering the profile template.
        user_data = {
            "username": user.username,
            "email": user.email,
            "avatar": user.avatar,
            "bio": user.bio,
            "gender": user.gender,
            "location": user.location,
            "fname": user.fname,
            "lname": user.lname,
            "ranking": ranking,
            "time": time,
            "personality": user.personality
        }
        
        # Render the profile template with user data.
        return render_template('1.html', user_data=user_data)

@app.route('/api/editimage', methods=["POST"])
@login_required
def editimage():
    if not request.files or 'image' not in request.files:
        # Check if the request contains a file with the key 'image'.
        return jsonify({'message': 'Invalid data'})
    
    image = request.files['image']

    # Get the file extension from the uploaded image.
    ext = os.path.splitext(image.filename)[1]
    
    if ext in ('.jpg', '.png', '.svg'):
        # Retrieve the current user.
        user = AuthUser.query.get(current_user.email)
        old_avatar = user.avatar

        # Delete the old image if it exists.
        if old_avatar:
            old_path = os.path.join(app.config['PATH_IMG'] + current_user.path, old_avatar)
            if os.path.exists(old_path):
                os.remove(old_path)

        # Generate a unique name for the new image.
        name_image = f"avatar_{os.urandom(16).hex()}"
        
        # Define the file path for the new image.
        filepath = os.path.join(app.config['PATH_IMG'] + current_user.path, f"{name_image}{ext}")
        
        # Save the uploaded image to the specified file path.
        image.save(filepath)
        
        # Update the user's profile with the new avatar name.
        i_dict = {'avatar': name_image + ext}
        user.updateprofile(**i_dict)
        db.session.commit()
    else:
        return jsonify({'message': 'File type not allowed'})

    return jsonify({'message': 'Image changed successfully', "redirect": url_for('profile')})

@app.route('/api/editprofile', methods=['POST'])
@login_required
def editprofile():
    # Check if the request data is in JSON format.
    if not request.json:
        return jsonify({'message': 'Invalid data'})

    # Define the required fields for the profile update.
    required_fields = ['fname', 'lname', 'username', 'bio', 'location']
    request_data = request.json

    # Check if all required data are present in required fields.
    for field in request_data:
        if field not in required_fields:
            return jsonify({'message': 'Invalid data'})

    # Get the current user's data from the database.
    user = AuthUser.query.get(current_user.email)

    # Extract and validate each field from the JSON data.
    new_fname = request.json.get('fname')
    if not (1 <= len(new_fname) <= 30):
        return jsonify({'message': 'Invalid data'})

    new_lname = request.json.get('lname')
    if not (1 <= len(new_lname) <= 30):
        return jsonify({'message': 'Invalid data'})

    new_username = request.json.get('username')
    if not (1 <= len(new_username) <= 30):
        return jsonify({'message': 'Invalid data'})

    new_bio = request.json.get('bio')
    if not (len(new_bio) <= 300):
        return jsonify({'message': 'Invalid data'})

    new_location = request.json.get('location')
    if not (len(new_location) <= 50):
        return jsonify({'message': 'Invalid data'})

    # Update user data if any field has changed.
    if new_fname != user.fname:
        user.fname = new_fname

    if new_lname != user.lname:
        user.lname = new_lname

    if new_username != user.username:
        user.username = new_username

    if new_bio != user.bio:
        user.bio = new_bio

    if new_location != user.location:
        user.location = new_location

    try:
        # Commit the changes to the database.
        db.session.commit()
    except Exception as e:
        return jsonify({'message': str(e)})

    # Return a success message along with a redirect URL to the user's profile.
    return jsonify({'message': 'successfully', "redirect": url_for('profile')})

@app.route('/api/changepassword', methods=['POST'])
@login_required
def changepassword():
    # Check if the request contains valid JSON data and the required fields.
    if not request.json or not ('oldpassword' in request.json and 'password' in request.json and 'confirmpassword' in request.json):
        return jsonify({'message': 'Invalid data'})
    
    # Retrieve data from the JSON request.
    data = request.json
    old_password = data.get('oldpassword')
    new_password = str(data.get('password'))
    confirm_password = str(data.get('confirmpassword'))

    # Check if the current user is allowed to change their password.
    if current_user.check:
        return jsonify({'message': 'Password cannot be edited.'})
    
    # Check if the new password and the confirm password match.
    if new_password != confirm_password:
        return jsonify({'message': 'Passwords do not match.'})

    # Check if the old password matches the current user's password.
    if not check_password_hash(current_user.password, old_password):
        return jsonify({'message': 'Incorrect old password.'})
    
    if not password_check(new_password):
        # If there's at least one error, return a generic error message.
        return jsonify({'message': 'Invalid password.'})

    # Hash the new password using the scrypt method.
    validated_dict = {
        "password" : generate_password_hash(new_password, method='scrypt')
        }
    
    # Update the user's password in the database.
    user = AuthUser.query.get(current_user.email)
    user.update_password(**validated_dict)
    
    # Commit the changes to the database.
    db.session.commit()

    return jsonify({'message': 'successfully changed password'})

@app.route('/api/deleteaccount', methods=['POST'])
@login_required
def deleteaccount():
    # Check if the request contains valid JSON data and if the 'password' field is present.
    if not request.json or not 'password' in request.json:
        return jsonify({'message': 'Invalid data'})
    
    # Retrieve the password from the JSON request.
    data = request.json
    password = str(data.get('password'))
    
    # Verify if the provided password matches the current user's password.
    if not check_password_hash(current_user.password, password):
        return jsonify({'message': 'Password is not correct'})

    # Retrieve the user's private path.
    path = current_user.path

    # Delete user-related files and directories.
    shutil.rmtree(os.path.join(app.config['PATH_VIDEO'], path))
    shutil.rmtree(os.path.join(app.config['PATH_IMG'], path))
    shutil.rmtree(os.path.join(app.config['PATH_FILE'], path))

    # Delete user-related database records.
    Privatescore.query.filter_by(owner_email=current_user.email).delete()
    AuthUser.query.filter_by(email=current_user.email).delete()
    
    # Commit the changes to the database.
    db.session.commit()

    # Return a success message and a redirect URL to the home page.
    return jsonify({'message': 'Account successfully deleted', "redirect": url_for('newbase')})

@app.route('/img/<filename>')
@login_required
def img(filename):
    # Retrieve the user based on the avatar filename.
    user = AuthUser.query.filter_by(avatar=filename).first()

    # If the user does not exist, return a 404 error.
    if not user:
        abort(404)

    # Retrieve the user's private path.
    path = user.path

    # Construct the folder path for the user's images.
    folder_path = os.path.join(app.config['PATH_IMG'], path)

    # Serve the image from the specified directory.
    return send_from_directory(folder_path, filename)

# ----------------------------------------------------------------------otp---------------------------------------------------------------------
def send_email_in_background(recipient_email, otp):
    try:
        # SMTP server and port for Gmail.
        SMTP_SERVER = 'smtp.gmail.com'
        SMTP_PORT = 587

        # Your Gmail credentials.
        GMAIL_USERNAME = app.config['GMAIL_USERNAME']
        GMAIL_PASSWORD = app.config['GMAIL_PASSWORD']

        # Email message content.
        message = f"Dear Sir/Madam,\n\nThis is to inform you that a One-Time Password (OTP) has been generated for accessing the form. The OTP is: {otp}. Kindly ensure that you utilize this OTP within the next 60 seconds for security purposes. Please refrain from sharing this OTP with anyone.\n\nThank you."

        # Create an email message.
        msg = MIMEText(message)
        msg['From'] = GMAIL_USERNAME
        msg['To'] = recipient_email
        msg['Subject'] = 'OTP Verification'

        # Connect to the SMTP server, start TLS, login, send the email, and quit.
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(GMAIL_USERNAME, GMAIL_PASSWORD)
        server.sendmail(GMAIL_USERNAME, [recipient_email], msg.as_string())
        server.quit()
    except Exception as e:
        # Handle exceptions that may occur during the email sending process.
        print('An error occurred while sending the email:', str(e))

def generate_otp():
    OTP_KEY = pyotp.random_base32()
    session['OTP_KEY'] = OTP_KEY
    otp = pyotp.TOTP(OTP_KEY,interval=120)
    return otp.now()

@app.route('/api/getmail', methods=["POST"])
def formmail():
    if not request.json or not 'email' in request.json:
        return jsonify({'message': 'Invalid data'})
    
    recipient_email = request.json['email']
    user = AuthUser.query.filter_by(email=recipient_email).first()
    if user:
        otp = generate_otp()
        session['generated_otp'] = otp
        session['recipient_email'] = recipient_email
        email_thread = threading.Thread(target=send_email_in_background, args=(recipient_email, otp))
        email_thread.start()
        return jsonify({'message': 'Your email Success.'})
    else:
        return jsonify({'message': 'Please check your email.'})

@app.route('/api/otp', methods=["POST"])
def otp():
    # Check if 'generated_otp' exists in the session.
    if 'generated_otp' not in session:
        return jsonify({'message': 'Please fill email.'})
    
    # Check if the request contains valid JSON data and if 'otp' is present.
    if not request.json or not 'otp' in request.json:
        return jsonify({'message': 'Invalid data'})
    
    # Retrieve the OTP entered by the user from the request.
    user_entered_otp = request.json['otp']
    
    # Retrieve the generated OTP and OTP key from the session.
    generated_otp = session['generated_otp']
    otp_key = session['OTP_KEY']

    # Create an OTP instance with the stored OTP key and a 90-second interval.
    otp_instance = pyotp.TOTP(otp_key, interval=120)

    # Verify if the user-entered OTP matches the OTP generated by the server.
    if otp_instance.verify(user_entered_otp, valid_window=1) and generated_otp == user_entered_otp:
        # If the OTP is valid, set the 'check' session flag.
        session.pop('generated_otp', None)
        session.pop('OTP_KEY', None)
        session['check'] = True

        session_expiration_time = time.time() + SESSION_TIMEOUT
        session['session_expiration_time'] = session_expiration_time

        return jsonify({'message': 'successfully verified OTP'})
    else:
        return jsonify({'message': 'Invalid OTP'})

@app.route('/forgotpassword', methods=["GET", "POST"])
def forgotpassword():
    if request.method == 'POST':
        # Check if 'check' exists in the session, indicating that a valid email has been provided.
        if 'check' not in session:
            return jsonify({'message': 'Please fill email.'})
        
        # Check if the request contains valid JSON data and if 'password' is present.
        if not request.json or not 'password' in request.json:
            return jsonify({'message': 'Invalid data'})
        
        # Retrieve the new password from the JSON request.
        password = request.json['password']
        
        # Clear the session data related to email and session expiration time.
        session.pop('session_expiration_time', None)
        session.pop('check', None)

        # Validate the new password using a 'password_check' function (not shown).
        # You can implement this function to enforce password requirements.
        if not password_check(password):
            # If there's at least one error, return a generic error message.
            return jsonify({'message': 'Invalid password.'})

        # Hash the new password using the 'scrypt' method.
        validated_dict = {
            "password" : generate_password_hash(password, method='scrypt')
        }

        # Retrieve the recipient's email from the session.
        recipient_email = session.get('recipient_email')

        # Retrieve the user based on the recipient's email.
        user = AuthUser.query.filter_by(email=recipient_email).first()

        # Update the user's password in the database.
        user.update_password(**validated_dict)
        db.session.commit()

        # Clear the recipient email from the session.
        session.pop('recipient_email', None)

        # Return a success message and a redirect URL to the home page.
        return jsonify({'message': 'Password reset successfully', "redirect": url_for('newbase')})

    # Handle the GET request by rendering a template for the password reset form.
    return render_template('forgotpassword.html')

# ----------------------------------------------------------------------score and topscore---------------------------------------------------------------------
@app.route('/scoreboard')
@login_required
def scoreboard():
    # Set the initial page number and sorting criteria.
    Npage = 1
    sortscore = 'score'
    
    # Call the 'getscore' function to retrieve scoreboard details, pagination, and more.
    details, pagination, prev_num, next_num, page = getscore(Npage, sortscore)
    
    # Call the 'getscoretop' function to retrieve the top scores for the game.
    game_top = getscoretop(sortscore)
    # Render the 'scoreboard.html' template with the obtained data.
    
    return render_template('scoreboard.html', details=details, pagination=pagination,
                           prev_num=prev_num, next_num=next_num, page=page, game_top=game_top)

@app.route('/toggleid', methods=["POST"])
@login_required
def toggleid():
    if not 'sortscore' in request.json:
        return jsonify({'message': 'Invalid data'})
    
    Npage = int(request.json['page'])
    sortscore = request.json['sortscore']

    dict_v = ['Score', 'Date', 'Time', 'Speed']

    if not sortscore in dict_v:
        return jsonify({'message': 'Invalid data'})
    
    details, pagination, prev_num, next_num, page = getscore(Npage, sortscore.lower())
    pagination = list(pagination)

    return jsonify({'message': 'successfully updated', 'details': details, 'pagination': pagination,
                    'prev_num': prev_num, 'next_num': next_num, 'page': page})

@app.route('/toggleidtop', methods=["POST"])
@login_required
def toggleidtop():
    if not 'sortscore' in request.json:
        return jsonify({'message': 'Invalid data'})

    sortscore = request.json['sortscore']
    l_sort = (str(sortscore)).lower()
    dict_v = ['score','time','speed']

    if not l_sort in dict_v:
        return jsonify({'message': 'Invalid data'})
    
    game_top = getscoretop(l_sort)
    return jsonify({'message': 'successfully', 'game_top':game_top})

@app.route('/updatescore', methods=["POST"])
@login_required 
def updatescore():
    # Check if the request contains valid JSON data and if 'page' and 'sortscore' are present.
    if not request.json or not 'page' in request.json or not 'sortscore' in request.json:
        return jsonify({'message': 'Invalid data'})
    
    # Retrieve the page number and sorting criteria from the JSON request.
    Npage = int(request.json['page'])
    sortscore = request.json['sortscore']
    
    # Define a list of valid sorting criteria.
    dict_v = ['Score', 'Date', 'Time', 'Speed']

    # Check if the provided sorting criteria is valid.
    if not sortscore in dict_v:
        return jsonify({'message': 'Invalid data'})
    
    # Call the 'getscore' function to retrieve updated scoreboard details, pagination, etc.
    details, pagination, prev_num, next_num, page = getscore(Npage, sortscore.lower())
    pagination = list(pagination)
    
    # Return a JSON response with the updated scoreboard data.
    return jsonify({'message': 'successfully updated', 'details': details, 'pagination': pagination,
                    'prev_num': prev_num, 'next_num': next_num, 'page': page})

def getscoretop(sortscore):
    order_options = {
        'time': (Privatescore.time, asc),
        'speed': (Privatescore.speed, desc),
        'score': (Privatescore.score, desc)
    }
    order_column, order_direction = order_options[sortscore]

    game_details = Privatescore.query.order_by(order_direction(order_column)).limit(10).all()
    game_top = []

    for game in game_details:
        user = AuthUser.query.get(game.owner_email)
        x_value,y_value = find_graph_value(game.id)
        score_limit = [limit_score(limit)[0] for limit in game.zonelimit]
        crosswalk_val, roundabout_val = cal_cross_roundabout(game.pass_crosswalk, game.pass_roundabout)
        
        if game.distance == 100:
            game_top.append({
                'id': game.id,
                'time': game.time,
                'score': game.score,
                'roundabout': game.pass_roundabout,
                'crosswalk': game.pass_crosswalk,
                'crash_car': game.crash_car,
                'crash_platform': game.crash_platform,
                'speed': game.speed,
                'zonelimit': game.zonelimit,
                'overturn': game.overturn,
                'carbreak': game.carbreak,
                'username': user.username,
                'y_value':y_value,
                'x_value':x_value,
                'score_limit':score_limit,
                'roundabout_val':roundabout_val,
                'crosswalk_val':crosswalk_val
            })

    ranking = 1
    for rank in game_top:
        rank['rank'] = ranking
        ranking += 1
    return game_top

@app.route('/topscore', methods=["POST"])
@login_required
def topscore():
    if not request.json or not 'sortscore' in request.json:
        return jsonify({'message': 'Invalid data'})

    sortscore = request.json['sortscore']
    l_sort = (str(sortscore)).lower()
    dict_v = ['score','time','speed']

    if not l_sort in dict_v:
        return jsonify({'message': 'Invalid data'})
    
    game_top = getscoretop(l_sort)
    return jsonify({'message': 'successfully', 'game_top':game_top})

def getscore(page,selected_order):
    rows_per_page = 10
    order_options = {
        'time': (Privatescore.time, asc),
        'speed': (Privatescore.speed, desc),
        'score': (Privatescore.score, desc)
    }
    
    if selected_order in order_options:
        order_column, order_direction = order_options[selected_order]
    else:
        order_column, order_direction = Privatescore.datetime, desc
    game_info = Privatescore.query.filter_by(owner_email=current_user.email)\
                            .order_by(order_direction(order_column))\
                            .paginate(page=page, per_page=rows_per_page, error_out=False)

    detail = []
    for info in game_info.items:
        formatted_datetime = info.datetime.strftime("%Y-%m-%d %H:%M:%S")
        if info.distance != 100:
            rank = "-"
        else:
            rank = my_ranking(info.score)
        x_value,y_value = find_graph_value(info.id)
        score_limit = [limit_score(limit)[0] for limit in info.zonelimit]
        crosswalk_val, roundabout_val = cal_cross_roundabout(info.pass_crosswalk, info.pass_roundabout)
        
        detail.append({
                'time': info.time,
                'score': info.score,
                'roundabout': info.pass_roundabout,
                'crosswalk': info.pass_crosswalk,
                'crash_car': info.crash_car,
                'crash_platform': info.crash_platform,
                'speed': info.speed, 
                'zonelimit': info.zonelimit,
                'overturn': info.overturn,
                'carbreak': info.carbreak,
                'datetime' : formatted_datetime,
                'id': info.id,
                'rank': rank,
                'y_value':y_value,
                'x_value':x_value,
                'score_limit':score_limit,
                'roundabout_val':roundabout_val,
                'crosswalk_val':crosswalk_val
        })
    
    left_edge = 2
    right_edge = 2
    left_current = 2
    right_current = 2

    # left_edge = 2 if page < 6 else 8
    # left_current = 2 if page < 6 else 7 + (page - game_info.pages)
    # right_edge = 2 if page > game_info.pages - 6 else 8
    # right_current = 2 if page > game_info.pages - 6 else 7 + (page - game_info.pages)

    if page < 6:
        left_edge = 8
    elif page > game_info.pages - 6:
        left_current = 7 + (page - game_info.pages)

    pagination = game_info.iter_pages(
        left_edge=left_edge,
        right_edge=right_edge,
        left_current=left_current,
        right_current=right_current
    )
    prev_num = None if not game_info.has_prev else game_info.prev_num
    next_num = None if not game_info.has_next else game_info.next_num
    
    return detail, pagination, prev_num, next_num, page

def find_graph_value(id):
    x_value = []
    y_value = []

    score = Privatescore.query.filter_by(id=id).first()
    namepath = AuthUser.query.filter_by(email=score.owner_email).first().path
    file_path = os.path.join(app.config['PATH_FILE'] + namepath, score.json)

    try:
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
            key_value_pairs = data["graph"].items()
            for key, value in key_value_pairs:
                x_value.append(key)
                y_value.append(value)

    except FileNotFoundError:
        print(f"The file '{file_path}' was not found.")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON in '{file_path}': {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

    return x_value,y_value

def cal_cross_roundabout(crosswalk,roundabout):
    count = 0
    crosswalk_val = []
    for i in range(len(crosswalk)):
        if crosswalk[i] == 1:
            count += 1 
        if i == 2:
            crosswalk_val.append(count*300)
            count = 0
    crosswalk_val.append(count*300)

    count = 0
    roundabout_val = []
    for i in range(len(roundabout)):
        if roundabout[i] == 1:
            count += 1
        if i == 4:
            roundabout_val.append(count*180)
            count = 0
    roundabout_val.append(count*180)

    return crosswalk_val,roundabout_val

def my_ranking(my_score):
    # Query all scores from the 'Privatescore' table, ordered by descending score
    all_scores = Privatescore.query.filter_by(distance=100).order_by(desc('score')).all()
    
    # Initialize a variable to keep track of the ranking
    ranking = 0
    
    # Iterate through each score in the list of scores
    for score in all_scores:
        # Increment the ranking by 1 for each score encountered
        ranking += 1
        
        # Check if 'my_score' is greater than or equal to the current score
        if my_score >= score.score:
            # If 'my_score' is greater or equal, break out of the loop
            break
    
    # Return the calculated ranking of 'my_score' within the list of scores
    return ranking

def calscore(time,distance,crash_platform,crosswalk,roundabout,overturn,limit,personality_val):
    score = 0
    # cal distance
    if distance == 100:
        score += 500

    # cal time
    if time <= 240:
        score += 25/12 * time
    else:
        score += -(time-480)/12 * 25

    # cal personality_val
    score += 3000 - (6000*abs(0.5-personality_val))
 
    # cal pass crosswalk times each 300 sp point 200
    count = 0
    for i in range(len(crosswalk)):
        if crosswalk[i] == 1:
            count += 1  
    if count == 6:
        score += 200
    score += (count*300)

    # cal pass roundabout times each 180 sp point 200
    count = 0
    for i in range(len(roundabout)):
        if roundabout[i] == 1:
            count += 1
    if count == 10:
        score += 200    
    score += (count*180)

    # cal pass limit times each 300 sp point 200
    count = 0
    for lap in limit:
        score_all,count = limit_score(lap)
        score += score_all
        count += count
    if count == 6:
        score += 200   

    score_negative = 0
    score_negative += (overturn*750)
    score_negative += (crash_platform*250)

    if score_negative > 5000:
        score_negative = 5000

    score -= score_negative

    if score < 0:
        score = 0

    score = round(score,2)

    return score

def limit_pass(limits_list):
    pass_limit = []
    for limits in limits_list: 
        for i, limit in enumerate(limits):
            if i == 0 or i == 1:
                if limit <= 40:
                    pass_limit.append(1)
                else:
                    pass_limit.append(0)
            elif i == 2:
                if limit <= 60:
                    pass_limit.append(1)
                else:
                    pass_limit.append(0)
    return pass_limit

def limit_score(lap):
    score_all = 0
    count = 0
    for i in range (len(lap)):
        score = 300
        if i == 0 or i== 1:
            if lap[i] == 0:
                score = 0
            elif lap[i] >= 53:
                score -= 300
            elif lap[i] >= 51:
                score -= 280
            elif lap[i] >= 49:
                score -= 260
            elif lap[i] >= 47:
                score -= 240
            elif lap[i] >= 45:
                score -= 220
            elif lap[i] >= 43:
                score -= 200
            elif lap[i] >= 41:
                score -= 150
            else:
                count += 1
        elif i == 2:
            if lap[i] == 0:
                score = 0
            elif lap[i] >= 73:
                score -= 300
            elif lap[i] >= 71:
                score -= 280
            elif lap[i] >= 69:
                score -= 260
            elif lap[i] >= 67:
                score -= 240
            elif lap[i] >= 65:
                score -= 220
            elif lap[i] >= 63:
                score -= 200
            elif lap[i] >= 61:
                score -= 150
            else:
                count += 1

        score_all += score
    return score_all,count

def find_value(data):
    max_lap = 2
    limit = [[0] * 3 for _ in range(max_lap)]
    crosswalk = [0] * (3 * (max_lap))
    roundabout = [0] * (5 * (max_lap))

    map = {}
    speed_per_distance = {}

    prediction_roundabout_all = {}
    prediction_crosswalk_all = {}
    prediction_limit_all = {}

    dict_roundabout = {}
    dict_crosswalk = {}
    dict_limit = {}

    prediction_roundabout = []
    prediction_crosswalk = []
    prediction_limit = []

    roundabout_started = False
    roundabout_check = False  
 
    crosswalk_started = False

    count_Car_Crashed = 0
    count_Map_Crashed = 0
    count_car_Overturn = 0

    count_lap = 1
    count_sector = 1

    for _ , row in data.iterrows():
        speed = int(row["Speed"])
        lap = row["Lap"]
        sector = row["Sector"]
        time = int(row["Time"])
        roundabout_val = row["Passed Circus"]
        crosswalk_val = row["Passed Crosswalk"]
        Distance = int(row["Distance"])
        Map = row["Map Crashed"]
        Overturn = row["Car Overturned"]
        Crash = row["Car Crashed"]
        Speed_Zone = row["Speed Zone"]

        if lap > count_lap:
            map["lap"+str(lap-1)] = {
            "roundabout" : dict_roundabout,
            "crosswalk" : dict_crosswalk,
            "limit" : dict_limit
            }
            dict_roundabout = {}
            dict_crosswalk = {}
            dict_limit = {}
            count_lap = 2
        
        if Speed_Zone != 0:
            limit[lap - 1][Speed_Zone - 1] = max(limit[lap - 1][Speed_Zone - 1], speed)
        speed_per_distance[Distance] = speed

        if count_sector == Speed_Zone:
            dict_limit["limit_"+str(Speed_Zone)] = time

            if not not prediction_limit :
                prediction_limit_all["limit_"+str(lap)+"_"+str(Speed_Zone)] = prediction_limit
                prediction_limit = []
            
            if Speed_Zone == 3:
                count_sector = 1
            else :
                count_sector += 1

        if (count_Map_Crashed != Map or count_car_Overturn != Overturn) and not (P_speed in prediction_limit):
            prediction_limit.append(P_speed)

        if roundabout_val != 0 and not roundabout_started:
            dict_roundabout["roundabout_"+str(roundabout_val)] = time
            roundabout_val_old = roundabout_val
            roundabout_started = True

        if roundabout_started and roundabout_val == 0:
            roundabout_started = False
            roundabout_check = False
            if not not prediction_roundabout:
                prediction_roundabout_all["roundabout_"+str(roundabout_val_old)] = prediction_roundabout
                prediction_roundabout = []

        if roundabout_started:
            if (count_Map_Crashed != Map or count_car_Overturn != Overturn) and not (P_speed in prediction_roundabout):
                prediction_roundabout.append(P_speed)
            if count_Car_Crashed != Crash  and not (P_car in prediction_roundabout):
                prediction_roundabout.append(P_car)
        
        if  roundabout_val != 0 and speed == 0:
            roundabout[roundabout_val-1] = 0
            roundabout_check = True
        elif roundabout_val != 0 and speed != 0 and not roundabout_check:
            roundabout[roundabout_val-1] = 1

        if crosswalk_val != 0 and not crosswalk_started:
            dict_crosswalk["crosswalk_"+str(crosswalk_val)] = time
            crosswalk_val_old = crosswalk_val
            crosswalk_started = True
 
        if crosswalk_started and crosswalk_val == 0:
            crosswalk_started = False
            if not not prediction_crosswalk:
                prediction_crosswalk_all["crosswalk_"+str(crosswalk_val_old)] = prediction_crosswalk
                prediction_crosswalk = []
        
        if crosswalk_started:
            if (count_Map_Crashed != Map or count_car_Overturn != Overturn) and not (P_speed in prediction_crosswalk):
                prediction_crosswalk.append(P_speed)
        
        if crosswalk_val != 0 and speed == 0:
            crosswalk[crosswalk_val-1] = 1

        count_Map_Crashed = Map
        count_Car_Crashed = Crash
        count_car_Overturn = Overturn
        
    last_entry = data.iloc[-1]
    average_speed = float(round(data['Speed'].mean(),2))
    distance = int(last_entry["Distance"])
    crash_car = int(last_entry["Car Crashed"])
    crash_platform = int(last_entry["Map Crashed"])
    overturn = int(last_entry["Car Overturned"])
    carbreak = int(last_entry["Brake Times"])
    time = int(last_entry["Time"])

    map["lap"+str(lap)] = {
        "roundabout" : dict_roundabout,
        "crosswalk" : dict_crosswalk,
        "limit" : dict_limit
    }

    map["graph"] = speed_per_distance

    map["prediction"] = {
        "roundabout" : prediction_roundabout_all,
        "crosswalk" : prediction_crosswalk_all,
        "limit" : prediction_limit_all
    }

    if crash_platform != 0 or crash_car != 0:

        map["prediction"]["accident"] = "Beware"
    return average_speed,distance,crash_car,crash_platform,overturn,carbreak,limit,crosswalk,roundabout,time,map

@app.route('/api/score', methods=["POST"])
def api_score():
    api_key = request.headers.get('api_key')
    if not api_key or api_key not in app.config['API_KEY_SCORE']:
        return jsonify({'message': 'Invalid API key'})
    
    if 'json' not in request.files or 'csv' not in request.files:
        return jsonify({'message': 'check csv or json'})
    
    try:
        json_file1 = request.files['json']
        json_data1 = json.load(json_file1)

        if not all(key in json_data1 for key in ["email", "video1", "video2", "name_state"]):
            return jsonify({'message': 'Invalid data'})

        user = AuthUser.query.filter_by(email=json_data1['email']).first()
        if not user:
            return jsonify({'message': 'Do not have email'})

        name_state =  json_data1['name_state']

        csv_file = request.files['csv']
        df = pd.read_csv(csv_file)

        # Assuming personal_detection is a function you've defined elsewhere
        personality, personality_val = personal_detection(df)

    except Exception as e:
        # Handle exceptions here
        print(e)
        return jsonify({'message': 'An error occurred: {}'.format(str(e))})
    
    if "You cant finish the line" != personality:
        validated_dict = {"personality":personality}
        user = AuthUser.query.get(user.email)
        user.update_personality(** validated_dict)
        db.session.commit()

    name = f"json_{uuid.uuid4()}.json"

    average_speed,distance,crash_car,crash_platform,overturn,carbreak,limit,crosswalk,roundabout,time,map = find_value(df)
    score = round(calscore(time,distance,crash_platform,crosswalk,roundabout,overturn,limit,personality_val),0)

    namepath = user.path
    file_path = os.path.join(app.config['PATH_FILE'] + namepath, name)
    with open(file_path, "w") as json_file:
            json.dump(map, json_file)
            
    score_entry = Privatescore(
            video1=json_data1['video1'],
            video2=json_data1['video2'],
            json = name,
            owner_email=json_data1['email'],
            time = time,
            distance = distance,
            score = score,
            speed = average_speed, 
            overturn = overturn, 
            carbreak = carbreak, 
            crash_car = crash_car, 
            crash_platform = crash_platform, 
            pass_roundabout = roundabout, 
            pass_crosswalk = crosswalk, 
            zonelimit = limit,
            name_state = name_state,
        )

    db.session.add(score_entry)
    db.session.commit()

    info = Privatescore.query.filter_by(owner_email=json_data1['email']).order_by(desc('datetime')).limit(2).all() 

    score_compare = "None Compare"
    speed_compare = "None Compare"
    if len(info) == 2:
        score1 = info[0].score
        score2 = info[1].score
        speed1 = info[0].speed
        speed2 = info[1].speed
        if score2 != 0:
            score_compare = round((100 * (score1/score2)) - 100, 2)
        if speed2 != 0:
            speed_compare = round((100 * (speed1/speed2)) - 100, 2)

    print("final")
    return jsonify({'message': 'Data successfully processed', 'speed': average_speed, 'score': score, 'score_compare':score_compare, 'speed_compare':speed_compare})

# ----------------------------------------------------------------------video---------------------------------------------------------------------
@app.route('/newvideo')
def newvideo():
    return render_template('newvideo.html')

@app.route('/chart')
def chart():
    return render_template('dognutchart.html')

@app.route('/api/video', methods=["POST"])
def api_video():
    api_key = request.headers.get('api_key')

    if not api_key or api_key not in app.config['API_KEY_VIDEO']:
        return jsonify({'message': 'Invalid API key'})

    try:
        video1_file = request.files['video1']
        video2_file = request.files['video2']
    except KeyError:
        return jsonify({'message': 'Both video1 and video2 must be provided in the request'})

    for file in (video1_file, video2_file):
        if not file:
            return jsonify({'message': 'Both video1 and video2 must be provided in the request'})
    print(video1_file)
    print(video2_file)
    # Check file extensions
    allowed_extensions = ['.mp4']
    for file in (video1_file, video2_file):
        ext = os.path.splitext(file.filename)[1]
        if ext not in allowed_extensions:
            return jsonify({'message': f'Invalid file format for {file.filename}'})
    
    score = Privatescore.query.filter_by(video1=video1_file.filename).first()
    if not score:
        return jsonify({'message': 'Score not found'})
    else:
        owner_email = score.owner_email
        namepath = AuthUser.query.filter_by(email=owner_email).first()

        # Handle video1
        filepath_video1 = os.path.join(app.config['PATH_VIDEO'] + namepath.path, video1_file.filename)
        try:
            video1_file.save(filepath_video1)
        except Exception as e:
            return jsonify({'message': f'Error saving video1: {str(e)}'})

        # Handle video2
        filepath_video2 = os.path.join(app.config['PATH_VIDEO'] + namepath.path, video2_file.filename)
        try:
            video2_file.save(filepath_video2)
        except Exception as e:
            return jsonify({'message': f'Error saving video2: {str(e)}'})

    return jsonify({'message': 'successfully'})

@app.route('/video/<id>')
@login_required
def video(id):
    score = Privatescore.query.filter_by(id=id).first()
    if not score:
        abort(404)
    return render_template('video.html', video1=score.video1, video2=score.video2)


@app.route('/api/video_detail', methods=["POST"])
@login_required
def video_detail():
    if not request.json or not 'id' in request.json:
        return jsonify({'message': 'Invalid data'})

    id = request.json["id"]
    x_value = []
    y_value = []
    score = Privatescore.query.filter_by(id=id).first()
    if not score:
        abort(404)  # Score not found, return a 404 error

    namepath = AuthUser.query.filter_by(email=score.owner_email).first()
    file_path = os.path.join(app.config['PATH_FILE'] + namepath.path, score.json)

    try:
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)

        key_value_pairs = data["graph"].items()
        for key, value in key_value_pairs:
            x_value.append(key)
            y_value.append(value)

        pass_crosswalk = score.pass_crosswalk
        pass_roundabout = score.pass_roundabout
        pass_zonelimit = limit_pass(score.zonelimit)
        score_limit = []
        for limit in score.zonelimit:
            scorel, _ = limit_score(limit)
            score_limit.append(scorel)
    

        return jsonify({'message': 'successfully', 'x_value': x_value, 'y_value': y_value, 'lap1': data["lap1"], "lap2": data["lap2"],
                        "score_limit": score_limit, "pass_zonelimit": pass_zonelimit, "pass_roundabout": pass_roundabout, "pass_crosswalk": pass_crosswalk, "prediction": data["prediction"],"cae_crash": score.crash_car, "car_break": score.carbreak})
    except FileNotFoundError:
        abort(404)  # File not found, return a 404 error
    except json.JSONDecodeError as e:
        abort(500)  # Error decoding JSON, return a 500 error
    except Exception as e:
        abort(500)  # Other exceptions, return a 500 error

@app.route('/listvideo/<filename>')
@login_required
def listvideo(filename):
    users = AuthUser.query.all()
    for user in users:
        folder_path = os.path.join(app.config['PATH_VIDEO'], user.path)
        full_file_path = os.path.join(folder_path, filename)

        if os.path.exists(full_file_path):
            return send_from_directory(folder_path, filename)
    abort(404)
# ----------------------------------------------------------------------login/signup/signout---------------------------------------------------------------------
@app.route('/login', methods=['POST'])
def login():
    if not request.json:
        return jsonify({'message': 'Invalid data'})

    data = request.json
    if 'email' not in data or 'password' not in data or 'remember' not in data:
        return jsonify({'message': 'Invalid data'})
    
    email = data['email']
    password = str(data['password'])
    remember = data['remember']
    
    if not isinstance(remember, bool):
        return jsonify({'message': 'Invalid data'})

    user = AuthUser.query.filter_by(email=email).first()
    if not user:
        return jsonify({'message': 'Please check your email.'})
    elif not check_password_hash(user.password, password):
        return jsonify({'message': 'Please check your password.'})
    
    login_user(user, remember=remember)

    return jsonify({'message':'successfully',"redirect": url_for('newbase')})

def generate_otp_signup():
    OTP_KEY = pyotp.random_base32()
    session['OTP_KEY_signup'] = OTP_KEY
    otp = pyotp.TOTP(OTP_KEY,interval=120)
    
    return otp.now()

@app.route('/api/getmail_signup', methods=["POST"])
def getmail_signup():
    if not request.is_json:
        return jsonify({'message': 'Invalid data'})

    data = request.json

    if 'email' not in data:
        return jsonify({'message': 'Invalid data'})

    recipient_email = data['email']
    user = AuthUser.query.filter_by(email=recipient_email).first()
    
    if not user:
        otp = generate_otp_signup()
        session['generated_otp_signup'] = otp
        session['recipient_email_signup'] = recipient_email

        # Start a thread to send the email in the background
        email_thread = threading.Thread(target=send_email_in_background, args=(recipient_email, otp))
        email_thread.start()

        return jsonify({'message': 'successfully'})
    else:
        return jsonify({'message': 'Email address already exists.'})


@app.route('/api/otp_signup', methods=["POST"])
def otp_signup():
    if not request.is_json:
        return jsonify({'message': 'Invalid data'})
    
    data = request.json

    if 'otp' not in data or 'generated_otp_signup' not in session:
        return jsonify({'message': 'Invalid data'})

    user_entered_otp = data['otp']
    generated_otp = session['generated_otp_signup']
    otp_key = session['OTP_KEY_signup']

    otp_instance = pyotp.TOTP(otp_key, interval=120)

    if otp_instance.verify(user_entered_otp, valid_window=1) and generated_otp == user_entered_otp:
        session.pop('generated_otp_signup', None)
        session.pop('OTP_KEY_signup', None)
        session['check_signup'] = True

        session_expiration_time = time.time() + SESSION_TIMEOUT
        session['session_expiration_time_signup'] = session_expiration_time

        return jsonify({'message': 'successfully'})
    else:
        return jsonify({'message': 'Invalid OTP'})

    
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST' and session['check_signup']:
        # Check if the request contains JSON data
        if not request.is_json:
            return jsonify({'message': 'Invalid data'})

        data = request.json

        validated = True
        validated_dict = {}
        valid_keys = ['email', 'fname', 'lname', 'phone', 'gender', 'password', 'birthday', 'Password_repeat', 'username']

        # Validate and sanitize user input
        for key in data:
            if key not in valid_keys:
                continue

            value = data[key].strip()
            if not value or value == 'undefined':
                validated = False
                break
            validated_dict[key] = value

        if validated:
            # Validate first name and last name length
            for key in ['fname', 'lname', 'username']:
                value = validated_dict[key]
                if not (1 <= len(value) <= 30):
                    return jsonify({'message': f'Invalid {key} length.'})
            
            # Validate phone number
            new_phone = validated_dict['phone']
            if not (len(new_phone) == 10 and new_phone.isdigit()):
                return jsonify({'message': f'Invalid phone number.'})

            # Validate password length
            new_password = validated_dict['password']
            if not (6 <= len(new_password) <= 30):
                return jsonify({'message': 'Invalid password length.'})
            
            # Validate date format and gender
            try:
                datetime.strptime(validated_dict['birthday'], '%Y-%m-%d')
            except ValueError:
                return jsonify({'message': 'Invalid date format.'})
            
            current_time = datetime.now()

            birthday_datetime = datetime.strptime(validated_dict['birthday'], '%Y-%m-%d')

            if birthday_datetime > current_time:
                return jsonify({'message': 'Invalid birthday.'})

            if validated_dict['gender'] not in ('male', 'female'):
                return jsonify({'message': 'Invalid gender.'})

            email = validated_dict['email']
            password = validated_dict['password']
            Password_repeat = validated_dict['Password_repeat']
            user = AuthUser.query.filter_by(email=email).first()

            if user:
                return jsonify({'message': 'Email address already exists.'})
            elif password != Password_repeat:
                return jsonify({'message': 'Password and Password_repeat do not match.'})
            else:
                # Validate the password using the password_check function
                if not password_check(password):
                    # If there's at least one error, return a generic error message.
                    return jsonify({'message': 'Invalid password.'})

            # Generate a unique directory and avatar name
            directory = generate_password_hash(str(email), method='scrypt')
            random_hex = os.urandom(16).hex()
            avatar = f"avatar_{random_hex}.svg"

            # Create a folder in a separate thread
            threading.Thread(target=createfolder, args=(directory, avatar)).start()

            fname = validated_dict['fname']
            lname = validated_dict['lname'] 
            phone = validated_dict['phone']
            gender = validated_dict['gender']
            username = validated_dict['username']
            birthday = validated_dict['birthday']

            # Create a new user and add to the database
            new_user = AuthUser(email=email, fname=fname, lname=lname,
                                password=generate_password_hash(password, method='scrypt'),
                                avatar=avatar, check=False, phone=phone, gender=gender, birthday=birthday, username=username, path=directory)
            db.session.add(new_user)
            db.session.commit()

            # Log in the new user
            login_user(new_user)

            return jsonify({'message': 'successfully', "redirect": url_for('newbase')})

    return render_template('signup.html')

def download_avatar(path):
    svg_string = boringavatars.avatar(
    "Sacagawea",
    variant="beam",
    colors=random_hex_color(),
    title=False,
    size=40,
    square=True,
    )

    with open(path, "w") as f:
        f.write(svg_string)

def createfolder(directory,avatar):
    path = os.path.join(app.config['PATH_IMG'], directory)
    os.makedirs(path, exist_ok=True)

    path = os.path.join(app.config['PATH_IMG'], directory, avatar)
    download_avatar(path)

    path = os.path.join(app.config['PATH_VIDEO'], directory)
    os.makedirs(path, exist_ok=True)

    path = os.path.join(app.config['PATH_FILE'], directory)
    os.makedirs(path, exist_ok=True)

def random_hex_color():
    hex_colors = []
    for _ in range(5):
        red = random.randint(0, 255)
        green = random.randint(0, 255)
        blue = random.randint(0, 255)
        hex_color = "{:02X}{:02X}{:02X}".format(red, green, blue)
        hex_colors.append(hex_color)
    return hex_colors

@app.route('/logout')
@login_required
def logout():
   logout_user()
   return redirect(url_for('newbase'))

# ----------------------------------------------------------------------google---------------------------------------------------------------------
@app.route('/google/')
def google():
    oauth.register(
        name='google',
        client_id=app.config['GOOGLE_CLIENT_ID'],
        client_secret=app.config['GOOGLE_CLIENT_SECRET'],
        server_metadata_url=app.config['GOOGLE_DISCOVERY_URL'],
        client_kwargs={
            'scope': 'openid email profile'
        }
    )

    redirect_uri = url_for('google_auth', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@app.route('/google/auth/')
def google_auth():
    token = oauth.google.authorize_access_token()
    userinfo = token['userinfo']
    email = userinfo['email']
    user = AuthUser.query.filter_by(email=email).first()
    if not user:
        directory = generate_password_hash(str(email), method='scrypt')
        random_hex = os.urandom(16).hex()
        avatar = f"avatar_{random_hex}.svg"

        threading.Thread(target=createfolder, args=(directory,avatar)).start()

        if "family_name" in userinfo:
            fname = userinfo['given_name'][:30]
            lname = userinfo['family_name'][:30]
        else:
            fname = userinfo['given_name'][:30]
            lname = ""

        random_pass_len = 30
        password = ''.join(secrets.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits + string.punctuation)for i in range(random_pass_len))
        username = generate_username(5)[0]
        new_user = AuthUser(email=email, fname=fname, lname=lname, username=username,
                           password=generate_password_hash(password, method='scrypt'),
                           avatar=avatar, check=True, phone="", gender="", birthday=None,path=directory)
        
        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)

    return redirect('/')

def password_check(password):
    # Convert the password to a string.
    password = str(password)

    # Check for various password requirements.
    length_error = len(password) < 6
    uppercase_error = re.search(r"[A-Z]", password) is None
    lowercase_error = re.search(r"[a-z]", password) is None
    symbol_error = re.search(r"\W", password) is None

    # Determine if the password is valid based on the criteria.
    password_ok = not (length_error or uppercase_error or lowercase_error or symbol_error)
    
    return password_ok

# ----------------------------------------------------------------------login_game---------------------------------------------------------------------
@app.route('/api/logingame', methods=['POST'])
def login_game():
    api_key = request.headers.get('api_key')
    if not api_key or api_key not in app.config['API_KEY_LOGIN']:
        return jsonify({'message': 'Invalid API key'})

    if not request.json:
        return jsonify({'message': 'Invalid data'})

    data = request.json
    if 'email' not in data or 'password' not in data:
        return jsonify({'message': 'Invalid data'})
    
    email = data['email']
    password = str(data['password'])

    user = AuthUser.query.filter_by(email=email).first()
    if not user:
        return jsonify({'message': 'Please check your email.'})
    elif not check_password_hash(user.password, password):
        return jsonify({'message': 'Please check your password.'})

    return jsonify({'message':'successfully','username':user.username})