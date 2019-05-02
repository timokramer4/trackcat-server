###########################
###       Imports       ###
###########################

from flask import Flask, flash, request, render_template, redirect, jsonify, session
from flaskext.mysql import MySQL
import simplejson
import time
import os
import json
from mailSend import sendVmail
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user


###########################
###    Configuration    ###
###########################

app = Flask(__name__)
mysql = MySQL()

app.secret_key = os.urandom(12)
app.config['MYSQL_DATABASE_USER'] = 'remRoot'
app.config['MYSQL_DATABASE_PASSWORD'] = '1Qayse45&'
app.config['MYSQL_DATABASE_DB'] = 'TrackCatDB'
app.config['MYSQL_DATABASE_HOST'] = 'safe-harbour.de'
app.config['MYSQL_DATABASE_PORT'] = 42042
mysql.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

###########################
###       Models        ###
###########################

# Logged user model


class User(UserMixin):

    def __init__(self, id, idUser, firstName, lastName, gender, img, dateOfBirth, dateOfRegistration, lastLogin):
        self.id = id
        self.idUser = idUser
        self.firstName = firstName
        self.lastName = lastName
        self.gender = gender
        self.img = img
        self.dateOfBirth = dateOfBirth
        self.dateOfRegistration = dateOfRegistration
        self.lastLogin = lastLogin


###########################
###      Test-Area      ###
###########################

@login_manager.user_loader
def user_loader(email):
    jsonUser = getUserFromDB(email)
    user = User(jsonUser['email'], jsonUser['id'],
                jsonUser['firstName'], jsonUser['lastName'], 
                jsonUser['gender'], jsonUser['image'], jsonUser['dateOfBirth'], 
                jsonUser['dateOfRegistration'], jsonUser['lastLogin'])
    return user

###########################
###      Functions      ###
###########################

# Validate login data


def validateLogin(email, password):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE email = '" + email + "';")
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result is not None and password == result[0]

# Basic Authentificate


def authenticate():
    message = {'message': "Authenticate."}
    resp = jsonify(message)
    resp.status_code = 401
    resp.headers['WWW-Authenticate'] = 'Basic realm="Main"'

    # return resp
    jsonObj = {}
    jsonObj['success'] = 1
    jsonObj['userData'] = None
    return json.dumps(jsonObj)


def requires_authorization(f):
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not validateLogin(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

# Create new user in database


def registerUserDB(firstName, lastName, email, password):
    # 0 = Valid
    # 1 = Creation error
    # 3 = Email already exists

    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (firstName, lastName, email, password, dateOfRegistration, lastLogin, darkTheme, hints, timeStamp) VALUES ('" +
                       firstName + "', '" + lastName + "', '" + email + "', '" + password + "', " + str(int(time.time())) + ", " +
                       str(int(time.time())) + ", 0, 1, "+str(int(time.time())) + ");")
        conn.commit()
        cursor.close()
        conn.close()
        pass
    except Exception as identifier:
        print(identifier)

        if(identifier.args[0] == 1062):
            if('eMail_UNIQUE' in identifier.args[1]):
                return 3
            return 1
    pass

    # TODO generate add link
    sendVmail(email, firstName, "http://safe-harbour.de:4242")
    return 0

# Get selected user from database as JSON


def getUserFromDB(email):
    conn = mysql.connect()
    cursor = conn.cursor()
    params = "id, email, firstName, lastName, password, image, dateOfBirth, gender, weight, size, darkTheme, hints, dateOfRegistration, lastLogin"
    cursor.execute("SELECT " + params +
                   " FROM users WHERE email = '" + email + "';")
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    jsonUser = {}
    jsonUser['id'] = result[0]
    jsonUser['email'] = result[1]
    jsonUser['firstName'] = result[2]
    jsonUser['lastName'] = result[3]
    jsonUser['password'] = result[4]
    jsonUser['image'] = result[5]
    jsonUser['dateOfBirth'] = result[6]
    if result[7] == None:
        jsonUser['gender'] = 2
    else:
        jsonUser['gender'] = result[7]
    jsonUser['weight'] = result[8]
    jsonUser['size'] = result[9]
    jsonUser['darkTheme'] = result[10]
    jsonUser['hints'] = result[11]
    jsonUser['dateOfRegistration'] = result[12]
    jsonUser['lastLogin'] = result[13]

    return jsonUser


def updateUserLastLogin(email):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET lastLogin = " +
                       str(int(time.time())) + " WHERE email = '" + email + "';")

        conn.commit()

        conn.close()
        pass
    except Exception as identifier:
        pass
    return


def updateUserDB(oldEmail, newEmail, dateOfBirth, firstName, lastName,
                 gender, size, weight, image):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()

        cursor.execute('UPDATE users SET email = "' + newEmail
                       + '", dateOfBirth = "' + dateOfBirth
                       + '", firstName = "' + firstName
                       + '", lastName = "' + lastName
                       + '", gender = "' + gender
                       + '", size = "' + size
                       + '", weight = "' + weight
                       + '", image = "' + image
                       + '" WHERE email = "' + oldEmail + '";')

        conn.commit()

        conn.close()
        pass
        return True
    except Exception as identifier:
        print(identifier)
        return False
        pass


###########################
###   WEB API-Handler   ###
###########################

# Start and login page
@app.route("/", methods=['GET'])
@app.route("/login", methods=['GET'])
def loginPage():
    if current_user.is_authenticated:
        return redirect("/dashboard")
    else:
        return render_template("login.html")

# LogOut user
@app.route("/logout", methods=['GET'])
def logoutPage():
    logout_user()
    return redirect("/login")

# Register page
@app.route("/register", methods=['GET'])
def registerPage():
    if current_user.is_authenticated:
        return redirect("/dashboard")
    else:
        return render_template("register.html")

# Profile page
@app.route("/dashboard", methods=["GET"])
def dashboardPage():
    if current_user.is_authenticated:
        return render_template("dashboard.html", user=current_user)
    else:
        return redirect("/login")

# Profile page
@app.route("/profile", methods=["GET"])
def profilePage():
    if current_user.is_authenticated:
        return render_template("profile.html", user=current_user)
    else:
        return redirect("/login")

# Profile page
@app.route("/settings", methods=["GET"])
def settingsPage():
    if current_user.is_authenticated:
        return render_template("settings.html", user=current_user)
    else:
        return redirect("/login")

### Web-Handler ###
@app.route("/login", methods=['POST'])
def login():
    # get user from db instantiate user
    if validateLogin(request.form['email'], request.form['password']):
        updateUserLastLogin(request.form['email'])
        user = user_loader(request.form['email'])
        login_user(user)
        return redirect("/dashboard")
    else:
        flash('Die eingegebenen Zugangsdaten sind falsch!')
        return redirect("/login")

# Register a user
@app.route("/registerUser", methods=['POST'])
def registerUser():
    # Add validation
    success = registerUserDB(
        request.form['firstName'], request.form['lastName'], request.form['email'], request.form['password1'])

    if success == 0:
        return redirect("/login")
    elif success == 1:
        flash('Unbekannter Fehler beim Erstelle des Kontos!')
        return redirect("/register")
    elif success == 3:
        flash('Die E-Mail Adresse existiert bereits!')
        return redirect("/register")

###########################
###  REST API-Handler   ###
###########################

# Check user login
@app.route("/loginAPI", methods=['POST'])
@requires_authorization
def loginAPI():
    updateUserLastLogin(request.authorization.username)

    jsonObj = {}
    jsonObj['success'] = 0
    jsonObj['userData'] = getUserFromDB(request.authorization.username)

    return json.dumps(jsonObj)

# Create new user in database
@app.route("/registerAPI", methods=['POST'])
def registerAPI():
    jsonRequest = request.json

    jsonObj = {}
    jsonObj['success'] = registerUserDB(
        jsonRequest['firstName'], jsonRequest['lastName'], jsonRequest['email'], jsonRequest['password'])


    return json.dumps(jsonObj)

# Get all userdata from user with email
@app.route("/getUserByEmailAPI", methods=['POST'])
def getUserByEmailAPI():
    return json.dumps(getUserFromDB(request.json['eMail']))


# Update user data in database
@app.route("/updateUserAPI", methods=['POST'])
def updateUser():
    j = request.json

    jsonSuccess = {}
    if updateUserDB(j['email'], j['email'], j['dateOfBirth'], j['firstName'], j['lastName'], j['gender'], j['size'], j['weight'], j['image']):
        jsonSuccess['success'] = 0
    else:
        jsonSuccess['success'] = 1

    return json.dumps(jsonSuccess)

@app.route("/synchronizeDataAPI", methods=['POST'])
def synchronizeDataAPI():
    conn = mysql.connect()
    cursor = conn.cursor()
    params = "timeStamp"
    cursor.execute("SELECT " + params +
                   " FROM users WHERE email = '" + request.json['email'] + "';")
    result = cursor.fetchone()
    cursor.close()
    conn.close() 

    jsonAnswer = {}

    if(int(request.json['timeStamp']) < result[0]):
        jsonAnswer['state'] = 0
        jsonAnswer['user'] = getUserFromDB(request.json['email'])
    elif (int(request.json['timeStamp']) == result[0]):
        jsonAnswer['state'] = 2
        jsonAnswer['user'] = None
    else:
        jsonAnswer['state'] = 1
        jsonAnswer['user'] = None

    return json.dumps(jsonAnswer)




###########################
###     Flask start     ###
###########################

if __name__ == '__main__':
    app.run(host='0.0.0.0')
