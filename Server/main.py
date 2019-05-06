###########################
###       Imports       ###
###########################

from flask import Flask, flash, request, render_template, redirect, jsonify, session, make_response, send_file
from flaskext.mysql import MySQL
import simplejson
import time
import os
import json
from mailSend import sendVmail
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user
from datetime import datetime
from functools import wraps
import base64
import io
from passlib.hash import pbkdf2_sha256
import random


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


# "http://192.186.178.52:5000"#
app.config['BASE_URL'] = "http://safe-harbour.de:4242"

# DB Table Names
app.config['DB_TABLE_USERS'] = "users"

# DB colum-names
app.config['DB_USERS_ID'] = "id"
app.config['DB_USERS_EMAIL'] = "email"
app.config['DB_USERS_FIRSTNAME'] = "firstName"
app.config['DB_USERS_LASTNAME'] = "lastName"
app.config['DB_USERS_PASSWORD'] = "password"
app.config['DB_USERS_IMAGE'] = "image"
app.config['DB_USERS_DATEOFBIRTH'] = "dateOfBirth"
app.config['DB_USERS_GENDER'] = "gender"
app.config['DB_USERS_WEIGHT'] = "weight"
app.config['DB_USERS_SIZE'] = "size"
app.config['DB_USERS_DARKTHEME'] = "darkTheme"
app.config['DB_USERS_HINTS'] = "hints"
app.config['DB_USERS_DATEOFREGISTRATION'] = "dateOfRegistration"
app.config['DB_USERS_LASTLOGIN'] = "lastLogin"
app.config['DB_USERS_TIMESTAMP'] = "timeStamp"
app.config['DB_USERS_VERIFYTOKEN'] = "verifyToken"


login_manager = LoginManager()
login_manager.init_app(app)

###########################
###       Models        ###
###########################

# Logged user model


class User(UserMixin):

    def __init__(self, id, idUser, firstName, lastName, gender, weight, size,  dateOfBirth, dateOfRegistration, lastLogin):
        self.id = id
        self.idUser = idUser
        self.firstName = firstName
        self.lastName = lastName
        self.gender = gender
        self.weight = weight
        self.size = size
        self.dateOfBirth = dateOfBirth
        self.dateOfRegistration = dateOfRegistration
        self.lastLogin = lastLogin


###########################
###      Test-Area      ###
###########################


###########################
###      Functions      ###
###########################

# Validate login data
@login_manager.user_loader
def user_loader(email):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute('SELECT ' + app.config['DB_USERS_ID'] +
                   ' FROM '+app.config['DB_TABLE_USERS'] + ' WHERE '+app.config['DB_USERS_EMAIL']+' = "' + email + '";')
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    jsonUser = getUserFromDB(result[0])
    user = User(jsonUser['email'], jsonUser['id'],
                jsonUser['firstName'], jsonUser['lastName'],
                jsonUser['gender'], jsonUser['weight'], jsonUser['size'], jsonUser['dateOfBirth'],
                jsonUser['dateOfRegistration'], jsonUser['lastLogin'])
    return user


def validateLogin(email, password):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute('SELECT ' + app.config['DB_USERS_PASSWORD'] +
                   ' FROM '+app.config['DB_TABLE_USERS'] +
                   ' WHERE ' + app.config['DB_USERS_EMAIL']
                   + ' = "' + email + '";')
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
    # return json.dumps(jsonObj)

    return make_response("", 401)


def requires_authorization(f):
    @wraps(f)
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

        baseUrl = app.config['BASE_URL']+"/verifyEmail?email="+email+"&token="

        token = generateVerifyToken(
            firstName, lastName, email)

        conn = mysql.connect()
        cursor = conn.cursor()

        cursor.execute('INSERT INTO '+app.config['DB_TABLE_USERS'] + ' ('+app.config['DB_USERS_FIRSTNAME']+', '+app.config['DB_USERS_LASTNAME']+', '+app.config['DB_USERS_EMAIL']+', '+app.config['DB_USERS_PASSWORD']+', '+app.config['DB_USERS_DATEOFREGISTRATION']+', '+app.config['DB_USERS_LASTLOGIN']+', '+app.config['DB_USERS_DARKTHEME']+', '+app.config['DB_USERS_HINTS']+', '+app.config['DB_USERS_TIMESTAMP']+', '+app.config['DB_USERS_VERIFYTOKEN']+') VALUES ("' +
                       firstName + '", "' + lastName + '", "' + email + '", "' + password + '", ' + str(int(time.time())) + ', ' +
                       str(int(time.time())) + ', 0, 1, '+str(int(time.time())) + ',"' + token + '");')

        conn.commit()
        cursor.close()
        conn.close()

        sendVmail(email, firstName,  baseUrl + token)
        return 0

    except Exception as identifier:
        print(identifier)

        if(identifier.args[0] == 1062):
            if('eMail_UNIQUE' in identifier.args[1]):
                return 3
        return 1
    pass


def generateVerifyToken(firstName, lastName, email):

    # if want to use custom iterations instead of default 29000
    #  custom_pbkdf2 = pbkdf2_sha256.using(rounds=123456)
    #   custom_pbkdf2.default_rounds
    # 123456

    #  custom_pbkdf2.hash("password")

    userData = [firstName, lastName, email]

    random.shuffle(userData)
    token = pbkdf2_sha256.hash(userData[0]+userData[1]+userData[2])

    return token

# Get selected user from database as JSON


def getUserFromDB(id):
    conn = mysql.connect()
    cursor = conn.cursor()
    params = app.config['DB_USERS_ID']+', '+app.config['DB_USERS_EMAIL']+', '+app.config['DB_USERS_FIRSTNAME']+', '+app.config['DB_USERS_LASTNAME']+', '+app.config['DB_USERS_PASSWORD']+', '+app.config['DB_USERS_DATEOFBIRTH']+', '+app.config['DB_USERS_GENDER']+', ' + \
        app.config['DB_USERS_WEIGHT']+', '+app.config['DB_USERS_SIZE']+', '+app.config['DB_USERS_DARKTHEME']+', '+app.config['DB_USERS_HINTS'] + \
        ', '+app.config['DB_USERS_DATEOFREGISTRATION']+', ' + \
        app.config['DB_USERS_LASTLOGIN']+', ' + \
        app.config['DB_USERS_TIMESTAMP']+''
    cursor.execute('SELECT ' + params +
                   ' FROM '+app.config['DB_TABLE_USERS'] + ' WHERE '+app.config['DB_USERS_ID']+' = "' + str(id) + '";')
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    jsonUser = {}
    jsonUser['id'] = result[0]
    jsonUser['email'] = result[1]
    jsonUser['firstName'] = result[2]
    jsonUser['lastName'] = result[3]
    jsonUser['password'] = result[4]
    jsonUser['dateOfBirth'] = result[5]
    if result[6] == None:
        jsonUser['gender'] = 2
    else:
        jsonUser['gender'] = result[6]
    jsonUser['weight'] = result[7]
    jsonUser['size'] = result[8]
    jsonUser['darkTheme'] = result[9]
    jsonUser['hints'] = result[10]
    jsonUser['dateOfRegistration'] = result[11]
    jsonUser['lastLogin'] = result[12]
    jsonUser['timeStamp'] = result[13]

    return jsonUser


def getUserWithImageFromDB(id):
    jsonUser = getUserFromDB(id)

    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute('SELECT '+app.config['DB_USERS_IMAGE']+' FROM '+app.config['DB_TABLE_USERS'] +
                   ' WHERE '+app.config['DB_USERS_ID']+' = "' + str(id) + '";')
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    jsonUser['image'] = result[0]

    return jsonUser

# Update last login in database


def updateUserLastLogin(email):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute('UPDATE ' + app.config['DB_TABLE_USERS']+' SET '+app.config['DB_USERS_LASTLOGIN']+' = ' +
                       str(int(time.time())) + ' WHERE '+app.config['DB_USERS_EMAIL']+' = "' + email + '";')

        conn.commit()

        conn.close()
        pass
    except Exception as identifier:
        pass
    return

# Update user informations in database


def updateUserDB(oldEmail, newEmail, dateOfBirth, firstName, lastName,
                 gender, size, weight, image, hints, darkTheme):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()

        try:
            cursor.execute('UPDATE '+app.config['DB_TABLE_USERS'] + ' SET '+app.config['DB_USERS_DATEOFBIRTH']+' =  "' + dateOfBirth
                           + '" WHERE '+app.config['DB_USERS_EMAIL']+' = "' + oldEmail + '";')
            pass
        except Exception as identifier:
            pass

        try:
            cursor.execute('UPDATE '+app.config['DB_TABLE_USERS'] + ' SET '+app.config['DB_USERS_FIRSTNAME']+' = "' + firstName
                           + '" WHERE '+app.config['DB_USERS_EMAIL']+' = "' + oldEmail + '";')
            pass
        except Exception as identifier:
            pass

        try:
            cursor.execute('UPDATE '+app.config['DB_TABLE_USERS'] + ' SET  '+app.config['DB_USERS_LASTNAME']+' = "' + lastName
                           + '" WHERE '+app.config['DB_USERS_EMAIL']+' = "' + oldEmail + '";')
            pass
        except Exception as identifier:
            pass

        try:
            cursor.execute('UPDATE '+app.config['DB_TABLE_USERS'] + ' SET '+app.config['DB_USERS_GENDER']+' = "' + gender
                           + '" WHERE '+app.config['DB_USERS_EMAIL']+' = "' + oldEmail + '";')
            pass
        except Exception as identifier:
            pass

        try:
            cursor.execute('UPDATE '+app.config['DB_TABLE_USERS'] + ' SET '+app.config['DB_USERS_SIZE']+' = "' + size
                           + '" WHERE '+app.config['DB_USERS_EMAIL']+' = "' + oldEmail + '";')
            pass
        except Exception as identifier:
            pass

        try:
            cursor.execute('UPDATE '+app.config['DB_TABLE_USERS'] + ' SET  '+app.config['DB_USERS_WEIGHT']+' = "' + weight
                           + '" WHERE '+app.config['DB_USERS_EMAIL']+' = "' + oldEmail + '";')
            pass
        except Exception as identifier:
            pass

        try:
            cursor.execute('UPDATE '+app.config['DB_TABLE_USERS'] + ' SET '+app.config['DB_USERS_IMAGE']+' = "' + image
                           + '" WHERE '+app.config['DB_USERS_EMAIL']+' = "' + oldEmail + '";')
            pass
        except Exception as identifier:
            pass

        try:
            cursor.execute('UPDATE '+app.config['DB_TABLE_USERS'] + ' SET '+app.config['DB_USERS_EMAIL']+' = "' + newEmail
                           + '" WHERE '+app.config['DB_USERS_EMAIL']+' = "' + oldEmail + '";')
            pass
        except Exception as identifier:
            pass

        try:
            cursor.execute('UPDATE '+app.config['DB_TABLE_USERS'] + ' SET '+app.config['DB_USERS_HINTS']+' = "' + hints
                           + '" WHERE '+app.config['DB_USERS_EMAIL']+' = "' + oldEmail + '";')
            pass
        except Exception as identifier:
            pass

        try:
            cursor.execute('UPDATE '+app.config['DB_TABLE_USERS'] + ' SET '+app.config['DB_USERS_DARKTHEME']+' = "' + darkTheme
                           + '" WHERE '+app.config['DB_USERS_EMAIL']+' = "' + oldEmail + '";')
            pass
        except Exception as identifier:
            pass

        conn.commit()

        conn.close()
        pass
        return True
    except Exception as identifier:
        print(identifier)
        return False
        pass

# Change user password in database


def changeUserPasswordDB(email, password, newPw, timeStamp):
    result = 0
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        params = "password"
        cursor.execute('SELECT ' + params +
                       ' FROM '+app.config['DB_TABLE_USERS'] + ' WHERE '+app.config['DB_USERS_EMAIL']+' = "' + email + '";')
        result = cursor.fetchone()

        if result[0] == password:
            cursor.execute('UPDATE '+app.config['DB_TABLE_USERS'] + ' SET '+app.config['DB_USERS_PASSWORD']+' = "' +
                           newPw + '", '+app.config['DB_USERS_TIMESTAMP']+' = ' + timeStamp + ' WHERE '+app.config['DB_USERS_EMAIL']+' = "' + email + '";')
            result = 0
        else:
            result = 1

        conn.commit()
        cursor.close()
        conn.close()
        return result

    except Exception as identifier:
        print(identifier)
        result = 2
        return result


def deleteUserById(id):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()

        cursor.execute('DELETE FROM ' + app.config['DB_TABLE_USERS'] +
                       ' WHERE '+app.config['DB_USERS_ID']+' = "' + str(id) + '";')

        conn.commit()
        cursor.close()
        conn.close()
        return 0
    except Exception as identifier:
        return 1


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
        alertType = request.args.get('alert')
        return render_template("login.html", alert=alertType)

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
        alertType = request.args.get('alert')
        return render_template("register.html", alert=alertType)

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
        alertType = request.args.get('alert')
        return render_template("settings.html", user=current_user, alert=alertType)
    else:
        return redirect("/login")

### Web-Handler ###
@app.route("/login", methods=['POST'])
def login():
    # get user from db instantiate user

    if validateLogin(request.form['email'], request.form['password']):
        user = user_loader(request.form['email'])

        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute('SELECT ' + app.config['DB_USERS_VERIFYTOKEN'] +
                       ' FROM '+app.config['DB_TABLE_USERS'] +
                       ' WHERE ' + app.config['DB_USERS_ID']
                       + ' = "' + str(user.idUser) + '";')
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        if result[0] != None:
            flash('Deine Email-Adresse ist noch nicht verifiziert. Bitte gehe in dein E-Mail Postfach und verifiziere die Echheit deiner Person.')
            return redirect("/login?alert=warning")
        else:
            updateUserLastLogin(request.form['email'])
            login_user(user)
            return redirect("/dashboard")
    else:
        flash('Die eingegebenen Zugangsdaten sind falsch!')
        return redirect("/login?alert=warning")
    
# Register a user
@app.route("/registerUser", methods=['POST'])
def registerUser():
    # Add validation
    success = registerUserDB(
        request.form['firstName'], request.form['lastName'], request.form['email'], request.form['password1'])

    if success == 0:
        flash('Ihr Konto wurde erstellt. Bitte überprüfen Sie Ihr E-Mail Postfach und bestätigen Sie Ihre Registrierung, '
              + 'um Zugang zu Ihrem Konto zu erhalten!')
        return redirect("/login?alert=success")
    elif success == 1:
        flash('Unbekannter Fehler beim Erstellen des Kontos!')
        return redirect("/register?alert=danger")
    elif success == 3:
        flash('Die E-Mail Adresse existiert bereits!')
        return redirect("/register?alert=warning")

# Update user informations
@app.route("/updateUser", methods=['POST'])
def updateUser():
    if current_user.is_authenticated:
        birthday = int(datetime.strptime(
            request.form['birthday'], "%Y-%m-%d").timestamp())
        success = updateUserDB(current_user.id, None, str(birthday),
                               request.form['firstName'], request.form['lastName'], request.form['genderRadio'], None, None, None, None, None)

        if success:
            flash('Profil wurde erfolgreich editiert!')
            return redirect("/settings?alert=success")
        else:
            flash('Unbekannter Fehler beim Bearbeiten der Profilinformationen')
            return redirect("/settings?alert=danger")
    else:
        return redirect("/login")

# Change user password
@app.route("/changePassword", methods=['POST'])
def changePassword():
    if current_user.is_authenticated:
        pw1 = request.form['newPass']
        pw2 = request.form['newPass2']
        if pw1 == pw2:
            success = changeUserPasswordDB(
                current_user.id, request.form['currentPass'], request.form['newPass'], str(int(time.time())))

            if success == 0:
                flash('Passwort wurde erfolgreich geändert!')
                return redirect("/settings?alert=success")
            elif success == 1:
                flash('Authentifizierung fehlgeschlagen!')
                return redirect("/settings?alert=danger")
            else:
                flash('Unbekannter Fehler beim Ändern des Passworts!')
                return redirect("/settings?alert=danger")
        else:
            flash('Die neu gewählten Passwörter stimmen nicht überein!')
            return redirect("/settings?alert=warning")
    else:
        return redirect("/login")

# Delete user account
@app.route("/deleteAccount", methods=['POST'])
def deleteAccount():
    if current_user.is_authenticated:
        success = deleteUserById(current_user.idUser)

        if success == 0:
            flash('Ihr Account wurde erfolgreich gelöscht!')
            logout_user()
            return redirect("/login?alert=success")
        else:
            flash('Unbekannter Fehler beim Löschen des Accounts!')
            return redirect("/settings?alert=danger")
    else:
        return redirect("/login")


@app.route("/image", methods=['GET'])
def getImage():
    try:
        email = request.args.get('userEmail')

        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT '+app.config['DB_USERS_IMAGE']+' FROM '+app.config['DB_TABLE_USERS'] + ' WHERE '+app.config['DB_USERS_EMAIL']+' = "' + email + '";')
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        imgFile = base64.b64decode(result[0])

        return send_file(io.BytesIO(imgFile),
                         mimetype='image/jpeg',
                         as_attachment=True,
                         attachment_filename='.jpg')

    except Exception as identifier:
        return send_file("./static/img/defaultUser.jpg", attachment_filename='.jpg')


@app.route("/verifyEmail", methods=['GET'])
def verifyEmail():
    email = request.args.get('email')
    token = request.args.get('token')

    try:
        conn = mysql.connect()
        cursor = conn.cursor()

        cursor.execute('UPDATE '+app.config['DB_TABLE_USERS'] + ' SET '+app.config['DB_USERS_VERIFYTOKEN']+' = NULL WHERE '+app.config['DB_USERS_EMAIL']+' = "' +
                       email + '" AND '+app.config['DB_USERS_VERIFYTOKEN']+' = "' + token + '";')

        conn.commit()
        cursor.close()
        conn.close()

        return render_template("verification.html", state=1)
        pass
    except Exception as identifier:
        return render_template("verification.html", state=0)
        pass


###########################
###  REST API-Handler   ###
###########################
# Check user login
@app.route("/loginAPI", methods=['POST'])
@requires_authorization
def loginAPI():
    updateUserLastLogin(request.authorization.username)

    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute('SELECT ' + app.config['DB_USERS_ID'] +
                   ', ' + app.config['DB_USERS_VERIFYTOKEN'] + ' FROM '+app.config['DB_TABLE_USERS'] + ' WHERE '+app.config['DB_USERS_EMAIL']+' = "' + request.authorization.username + '";')
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    jsonObj = {}
    jsonObj['userData'] = getUserWithImageFromDB(result[0])
    if result[1] == None:
        jsonObj['success'] = 0
    else:
        jsonObj['success'] = 2

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
@app.route("/getUserByIdAPI", methods=['POST'])
@requires_authorization
def getUserByIdAPI():

    return json.dumps(getUserWithImageFromDB(request.json['id']))


# Update user data in database
@app.route("/updateUserAPI", methods=['POST'])
@requires_authorization
def updateUserAPI():
    j = request.json

    jsonSuccess = {}

    try:
        email = j['email']
        pass
    except Exception as identifier:
        email = None
        pass

    try:
        newEmail = j['newemail']
        pass
    except Exception as identifier:
        newEmail = None
        pass

    try:
        dateOfBirth = j['dateOfBirth']
        pass
    except Exception as identifier:
        dateOfBirth = None
        pass

    try:
        firstName = j['firstName']
        pass
    except Exception as identifier:
        firstName = None
        pass

    try:
        lastName = j['lastName']
        pass
    except Exception as identifier:
        lastName = None
        pass

    try:
        gender = j['gender']
        pass
    except Exception as identifier:
        gender = None
        pass

    try:
        size = j['size']
        pass
    except Exception as identifier:
        size = None
        pass

    try:
        weight = j['weight']
        pass
    except Exception as identifier:
        weight = None
        pass

    try:
        image = j['image']
        pass
    except Exception as identifier:
        image = None
        pass

    try:
        hints = j['hints']
        pass
    except Exception as identifier:
        hints = None
        pass

    try:
        darkTheme = j['darkTheme']
        pass
    except Exception as identifier:
        darkTheme = None
        pass

    if updateUserDB(email, newEmail, dateOfBirth, firstName, lastName, gender, size, weight, image, hints, darkTheme):
        jsonSuccess['success'] = 0
    else:
        jsonSuccess['success'] = 1

    return json.dumps(jsonSuccess)

# Change user password
@app.route("/changeUserPasswordAPI", methods=['POST'])
@requires_authorization
def changeUserPasswordAPI():
    jsonSuccess = {}

    jsonSuccess['success'] = changeUserPasswordDB(request.authorization.username, request.authorization.password,
                                                  request.json['newPw'], request.json['timeStamp'])

    return json.dumps(jsonSuccess)


# Synchronize user data with app database
@app.route("/synchronizeDataAPI", methods=['POST'])
@requires_authorization
def synchronizeDataAPI():
    conn = mysql.connect()
    cursor = conn.cursor()
    params = "timeStamp"
    cursor.execute('SELECT ' + params +
                   ' FROM '+app.config['DB_TABLE_USERS'] + ' WHERE '+app.config['DB_USERS_EMAIL']+' = "' + request.json['email'] + '";')
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    jsonAnswer = {}

    if(int(request.json['timeStamp']) < result[0]):
        jsonAnswer['state'] = 0
        jsonAnswer['user'] = getUserWithImageFromDB(request.json['email'])
    elif (int(request.json['timeStamp']) == result[0]):
        jsonAnswer['state'] = 2
        jsonAnswer['user'] = None
    else:
        jsonAnswer['state'] = 1
        jsonAnswer['user'] = None

    return json.dumps(jsonAnswer)


@app.route("/deleteUserAPI", methods=['POST'])
@requires_authorization
def deleteUserAPI():
    jsonSuccess = {}
    jsonSuccess['success'] = deleteUserById(request.json['id'])

    return json.dumps(jsonSuccess)
###########################
###     Flask start     ###
###########################


if __name__ == '__main__':
    app.run(host='0.0.0.0')
