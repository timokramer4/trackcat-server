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
from datetime import datetime, timedelta
from functools import wraps
import base64
import io
from passlib.hash import pbkdf2_sha256
import random
from threading import Thread


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

# TABLE-NAMES
app.config['DB_TABLE_USERS'] = "users"
app.config['DB_TABLE_HAS_USERS'] = "users_has_users"
app.config['DB_TABLE_RECORDS'] = "records"
app.config['DB_TABLE_LIVE_RECORDS'] = "liveRecords"
app.config['DB_TABLE_LOCATIONS'] = "locations"

# COLUMN-NAMES: User
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

# COLUMN-NAMES: users_has_users (friends)
app.config['DB_USERS_HAS_USERS_ASKER'] = "asker"
app.config['DB_USERS_HAS_USERS_ASKED'] = "asked"
app.config['DB_USERS_HAS_USERS_DOF'] = "dateOfFriendship"
app.config['DB_USERS_HAS_USERS_AF'] = "areFriends"

# COLUMN-NAMES: Record
app.config['DB_RECORD_ID'] = "id"
app.config['DB_RECORD_NAME'] = "name"
app.config['DB_RECORD_TIME'] = "time"
app.config['DB_RECORD_DATE'] = "date"
app.config['DB_RECORD_TYPE'] = "type"
app.config['DB_RECORD_RIDETIME'] = "rideTime"
app.config['DB_RECORD_DISTANCE'] = "distance"
app.config['DB_RECORD_TIMESTAMP'] = "timeStamp"
app.config['DB_RECORD_USERS_ID'] = "users_id"
app.config['DB_RECORD_LOCATION_DATA'] = "locations"


# COLUMN-NAMES: Location
app.config['DB_LOCATION_LATITUDE'] = "latitude"
app.config['DB_LOCATION_LONGITUDE'] = "longitude"
app.config['DB_LOCATION_ALTITUDE'] = "altitude"
app.config['DB_LOCATION_TIME'] = "time"
app.config['DB_LOCATION_SPEED'] = "speed"
app.config['DB_LOCATION_RECORD_ID'] = "record_id"


# Android
app.config['ANDROID_LOCATION_RECORD_ID'] = "recordId"

login_manager = LoginManager()
login_manager.init_app(app)

###########################
###       Models        ###
###########################

# Logged user model


class User(UserMixin):

    def __init__(self, id, email, firstName, lastName, gender, weight, size, dateOfBirth, dateOfRegistration, lastLogin):
        self.id = id
        self.email = email
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

@app.template_filter('formatSeconds')
def formatSeconds(value):
    return str(timedelta(seconds=value))


@app.template_filter('formatDate')
def formatDate(value, format='%d.%m.%Y %H:%M:%S'):
    return datetime.fromtimestamp(value/1000).strftime(format)

# Validate login data
@login_manager.user_loader
def user_loaderlmgr(id):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute('SELECT ' + app.config['DB_USERS_ID'] +
                   ' FROM '+app.config['DB_TABLE_USERS'] + ' WHERE '+app.config['DB_USERS_ID']+' = "' + id + '";')
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    jsonUser = getUserFromDB(result[0])
    user = User(jsonUser['id'], jsonUser['email'],
                jsonUser['firstName'], jsonUser['lastName'],
                jsonUser['gender'], jsonUser['weight'], jsonUser['size'], jsonUser['dateOfBirth'],
                jsonUser['dateOfRegistration'], jsonUser['lastLogin'])
    return user


def user_loader(email):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute('SELECT ' + app.config['DB_USERS_ID'] +
                   ' FROM '+app.config['DB_TABLE_USERS'] + ' WHERE '+app.config['DB_USERS_EMAIL']+' = "' + email + '";')
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    jsonUser = getUserFromDB(result[0])
    user = User(jsonUser['id'], jsonUser['email'],
                jsonUser['firstName'], jsonUser['lastName'],
                jsonUser['gender'], jsonUser['weight'], jsonUser['size'], jsonUser['dateOfBirth'],
                jsonUser['dateOfRegistration'], jsonUser['lastLogin'])
    return user

# Validate user login


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


def registerUserDB(firstName, lastName, email, password, birthday, gender):
    # 0 = Valid
    # 1 = Creation error
    # 3 = Email already exists

    success = 1

    conn = mysql.connect()
    cursor = conn.cursor()
    try:

        baseUrl = app.config['BASE_URL']+"/verifyEmail?email="+email+"&token="

        token = generateVerifyToken(
            firstName, lastName, email)

        cursor.execute('INSERT INTO '+app.config['DB_TABLE_USERS'] + ' ('+app.config['DB_USERS_FIRSTNAME']+', '+app.config['DB_USERS_LASTNAME']+', '+app.config['DB_USERS_EMAIL']+', '+app.config['DB_USERS_PASSWORD']+', ' + app.config['DB_USERS_DATEOFBIRTH']+', ' + app.config['DB_USERS_GENDER']+', '+app.config['DB_USERS_DATEOFREGISTRATION']+', '+app.config['DB_USERS_LASTLOGIN']+', '+app.config['DB_USERS_DARKTHEME']+', '+app.config['DB_USERS_HINTS']+', '+app.config['DB_USERS_TIMESTAMP']+', '+app.config['DB_USERS_VERIFYTOKEN']+') VALUES ("' +
                       firstName + '", "' + lastName + '", "' + email + '", "' + password + '", "' + birthday + '", "' + gender + '", ' + str(int(time.time())) + ', ' + str(int(time.time())) + ', 0, 1, '+str(int(time.time())) + ',"' + token + '");')

        conn.commit()

        sendVmail(email, firstName,  baseUrl + token)
        success = 0

    except Exception as identifier:
        print(identifier)

        if(identifier.args[0] == 1062):
            if('eMail_UNIQUE' in identifier.args[1]):
                success = 3
        success = 1
    pass
    cursor.close()
    conn.close()

    return success

# Generate verify token


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

# Get selected user data as JSON


def getUserFromDB(id):
    conn = mysql.connect()
    cursor = conn.cursor()
    params = app.config['DB_USERS_ID']+', '+app.config['DB_USERS_EMAIL']+', '+app.config['DB_USERS_FIRSTNAME']+', '+app.config['DB_USERS_LASTNAME']+', '+app.config['DB_USERS_PASSWORD']+', '+app.config['DB_USERS_DATEOFBIRTH']+', '+app.config['DB_USERS_GENDER']+', ' + \
        app.config['DB_USERS_WEIGHT']+', '+app.config['DB_USERS_SIZE']+', '+app.config['DB_USERS_DARKTHEME']+', '+app.config['DB_USERS_HINTS'] + \
        ', '+app.config['DB_USERS_DATEOFREGISTRATION']+', ' + \
        app.config['DB_USERS_LASTLOGIN']+', ' + \
        app.config['DB_USERS_TIMESTAMP']+''
    cursor.execute('SELECT ' + params +
                   ' FROM '+app.config['DB_TABLE_USERS'] + ' WHERE '+app.config['DB_USERS_ID']+' = ' + str(id) + ';')
    result = cursor.fetchone()

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

    # not saved statistics total ridetime amout of records and total distance
    cursor.execute("SELECT " + app.config['DB_RECORD_DISTANCE'] + ", " + app.config['DB_RECORD_RIDETIME'] +
                   " FROM " + app.config['DB_TABLE_RECORDS'] + " WHERE users_id = " + str(result[0]) + ";")

    result = cursor.fetchall()

    totDist = 0
    totTime = 0
    for record in result:
        totDist += record[0]
        totTime += record[1]

    jsonUser['totalDistance'] = totDist
    jsonUser['totalTime'] = totTime
    jsonUser['amountRecords'] = len(result)

    cursor.close()
    conn.close()

    return jsonUser

# Get user profile image


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


def getUserId(email):
    conn = mysql.connect()
    cursor = conn.cursor()

    sql = 'SELECT ' + app.config['DB_USERS_ID'] + " FROM " + \
        app.config['DB_TABLE_USERS'] + " WHERE " + \
        app.config['DB_USERS_EMAIL'] + " = %s;"

    cursor.execute(sql, (email,))

    result = cursor.fetchone()

    cursor.close()
    conn.close()
    return result[0]


# Change user password in database
def changeUserPasswordDB(email, password, newPw, timeStamp):
    result = 0
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        params = app.config['DB_USERS_PASSWORD']
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

# Delete user account by id


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

# Update record informations in database


def updateRecordDB(recordId, newName, timestamp):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()

        try:
            cursor.execute('UPDATE ' + app.config['DB_TABLE_RECORDS'] + ' SET ' + app.config['DB_RECORD_NAME'] + ' = "' + newName + '", ' +
                           app.config['DB_RECORD_TIMESTAMP'] + ' = "' + str(timestamp) + '" WHERE ' + app.config['DB_RECORD_ID']+' = "' + str(recordId) + '";')
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

# Delete user account by id


def deleteRecordById(id):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()

        cursor.execute('DELETE FROM ' + app.config['DB_TABLE_RECORDS'] +
                       ' WHERE '+app.config['DB_RECORD_ID']+' = "' + str(id) + '";')

        conn.commit()
        cursor.close()
        conn.close()
        return 0
    except Exception as identifier:
        return 1

# Get all record from user (all or by paging)


def getRecordsByID(userId, page):
    conn = mysql.connect()
    cursor = conn.cursor()

    start = page * 10 - 10
    end = page * 10

    if page > 0:
        limitter = ' LIMIT ' + str(start) + ', ' + str(end)
    else:
        limitter = ''

    params = app.config['DB_RECORD_ID'] + ', ' + app.config['DB_RECORD_NAME'] + ', ' + app.config['DB_RECORD_TIME'] + ', ' + app.config['DB_RECORD_DATE'] + ', ' + app.config['DB_RECORD_TYPE'] + \
        ', ' + app.config['DB_RECORD_RIDETIME'] + ', ' + app.config['DB_RECORD_DISTANCE'] + \
        ', ' + app.config['DB_RECORD_TIMESTAMP'] + \
        ', ' + app.config['DB_RECORD_LOCATION_DATA']
    cursor.execute('SELECT ' + params + ' FROM ' + app.config['DB_TABLE_RECORDS'] +
                   ' WHERE ' + app.config['DB_RECORD_USERS_ID'] + ' = ' + str(userId) + limitter + ";")
    result = cursor.fetchall()

    cursor.close()
    conn.close()

    jsonRecords = []

    for res in result:
        jsonRecord = {}
        jsonRecord['id'] = res[0]
        jsonRecord['name'] = res[1]
        jsonRecord['time'] = res[2]
        jsonRecord['date'] = res[3]
        jsonRecord['type'] = res[4]
        jsonRecord['ridetime'] = res[5]
        jsonRecord['distance'] = res[6]
        jsonRecord['timestamp'] = res[7]
        jsonRecord['locations'] = res[8]

        jsonRecords.append(jsonRecord)

    return jsonRecords

# Get single record


def getSingleRecordByID(recordId):
    conn = mysql.connect()
    cursor = conn.cursor()

    params = app.config['DB_RECORD_ID'] + ', ' + app.config['DB_RECORD_NAME'] + ', ' + app.config['DB_RECORD_TIME'] + ', ' + app.config['DB_RECORD_DATE'] + ', ' + app.config['DB_RECORD_TYPE'] + ', ' + \
        app.config['DB_RECORD_RIDETIME'] + ', ' + app.config['DB_RECORD_DISTANCE'] + ', ' + app.config['DB_RECORD_TIMESTAMP'] + \
        ', ' + app.config['DB_RECORD_USERS_ID'] + \
        ', ' + app.config['DB_RECORD_LOCATION_DATA']
    cursor.execute('SELECT ' + params + ' FROM ' +
                   app.config['DB_TABLE_RECORDS'] + ' WHERE ' + app.config['DB_RECORD_ID'] + ' = ' + str(recordId) + ';')
    result = cursor.fetchall()

    cursor.close()
    conn.close()

    res = result[0]

    jsonRecord = {}
    jsonRecord['id'] = res[0]
    jsonRecord['name'] = res[1]
    jsonRecord['time'] = res[2]
    jsonRecord['date'] = res[3]
    jsonRecord['type'] = res[4]
    jsonRecord['ridetime'] = res[5]
    jsonRecord['distance'] = res[6]
    jsonRecord['timestamp'] = res[7]
    jsonRecord['owner'] = res[8]

    #jsonRecordData = {}
    # jsonRecordData['record'] = jsonRecord #TODO remove
    # getLocationsByID(userId, recordId) switch from locations to json in db
    jsonRecord['locations'] = json.loads(res[9])

    return jsonRecord

# Get all locations from user (and from specific route)


def getLocationsByID(userId, recordId):
    conn = mysql.connect()
    cursor = conn.cursor()

    if recordId is not None:
        selection = app.config['DB_TABLE_RECORDS'] + '.' + \
            app.config['DB_RECORD_ID'] + ' = ' + str(recordId)
    else:
        selection = app.config['DB_TABLE_RECORDS'] + '.' + \
            app.config['DB_RECORD_USERS_ID'] + ' = ' + str(userId)

    params = app.config['DB_LOCATION_LATITUDE'] + ', ' + app.config['DB_LOCATION_LONGITUDE'] + ', ' + app.config['DB_LOCATION_ALTITUDE'] + ', ' + \
        app.config['DB_TABLE_LOCATIONS'] + '.' + app.config['DB_LOCATION_TIME'] + ', ' + \
        app.config['DB_LOCATION_SPEED'] + ', ' + \
        app.config['DB_LOCATION_RECORD_ID']
    cursor.execute('SELECT ' + params + ' FROM ' + app.config['DB_TABLE_LOCATIONS'] + ' INNER JOIN ' + app.config['DB_TABLE_RECORDS'] + ' ON ' + app.config['DB_TABLE_LOCATIONS'] +
                   '.' + app.config['DB_LOCATION_RECORD_ID'] + ' = ' + app.config['DB_TABLE_RECORDS'] + '.' + app.config['DB_RECORD_ID'] + ' AND ' + selection + ';')
    result = cursor.fetchall()

    cursor.close()
    conn.close()

    jsonLocations = []

    for res in result:
        jsonLocation = {}
        jsonLocation['lat'] = res[0]
        jsonLocation['lng'] = res[1]
        jsonLocation['altitude'] = res[2]
        jsonLocation['time'] = res[3]
        jsonLocation['speed'] = res[4]
        jsonLocation['record_id'] = res[5]

        jsonLocations.append(jsonLocation)

    return jsonLocations


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
        return render_template("dashboard.html", user=current_user, site="dashboard")
    else:
        return redirect("/login")

# Profile page
@app.route("/profile", methods=["GET"])
def profilePage():
    if current_user.is_authenticated:
        userId = request.args.get('id')

        if userId:
            try:
                userData = getUserFromDB(userId)
                pass
            except Exception as identifier:
                userData = None
                pass
            return render_template("profile.html", user=userData, back="/friends")
        else:
            return render_template("profile.html", user=current_user, back="/dashboard")
    else:
        return redirect("/login")

# Profile page
@app.route("/settings", methods=["GET"])
def settingsPage():
    if current_user.is_authenticated:
        alertType = request.args.get('alert')
        return render_template("settings.html", user=current_user, alert=alertType, back="/dashboard")
    else:
        return redirect("/login")

# AGB page
@app.route("/agb", methods=["GET"])
def agbPage():
    return render_template("agb.html")

# Data protection page
@app.route("/datenschutz", methods=["GET"])
def dataProtectionPage():
    return render_template("datenschutz.html")

# Show record list
@app.route("/records", methods=["GET"])
def recordsPage():
    if current_user.is_authenticated:
        records = getRecordsByID(current_user.id, 1)
        alertType = request.args.get('alert')
        return render_template("records.html", user=current_user, site="records", records=records, alert=alertType)
    else:
        return redirect("/login")

# Show record list
@app.route("/record", methods=["GET"])
def singleRecordPage():
    if current_user.is_authenticated:
        recordId = request.args.get('id')

        try:
            recordData = getSingleRecordByID(recordId)
            if recordData['owner'] != current_user.id:
                recordData = None
            pass
        except Exception as identifier:
            recordData = None
            pass

        alertType = request.args.get('alert')
        return render_template("single-record.html", user=current_user, recordData=recordData, alert=alertType, back="/records")
    else:
        return redirect("/login")

# Show record list
@app.route("/community/friends", methods=["GET"])
def friendsPage():
    if current_user.is_authenticated:
        friends = getRecordsByID(current_user.id, 1)
        alertType = request.args.get('alert')
        return render_template("friends.html", user=current_user, site="friends", friends=friends, alert=alertType)
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
                       + ' = ' + str(user.id) + ';')
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        if result[0] != None:
            flash('Ihre E-Mail Adresse ist noch nicht verifiziert. Bitte gehen Sie in Ihr E-Mail Postfach und verifiziere Sie damit die Echtheit Ihrer E-Mail Adresse.')
            return redirect("/login?alert=warning")
        else:
            updateUserLastLogin(request.form['email'])
            login_user(user)
            return redirect("/dashboard")
    else:
        flash('Ihre Anmeldedaten sind nicht korrekt!')
        return redirect("/login?alert=warning")

# Register a user
@app.route("/registerUser", methods=['POST'])
def registerUser():
    # Add validation
    success = registerUserDB(
        request.form['firstName'], request.form['lastName'], request.form['email'], request.form['password1'], request.form['birthday'], request.form['genderRadio'], request.form['size'], request.form['weight'])

    if success == 0:
        flash('Ihr Konto wurde erfolgreich erstellt. Bitte überprüfen Sie Ihr E-Mail Postfach und bestätigen Sie Ihre Registrierung, '
              + 'um Zugang zu Ihrem Konto zu erhalten!')
        return redirect("/login?alert=success")
    elif success == 1:
        flash('Unbekannter Fehler beim Erstellen des Kontos!')
        return redirect("/register?alert=danger")
    elif success == 3:
        flash('Es tut uns leid, ihre E-Mail Adresse ist leider schon vergeben!')
        return redirect("/register?alert=warning")

# Update user informations
@app.route("/updateUser", methods=['POST'])
def updateUser():
    if current_user.is_authenticated:
        birthday = int(datetime.strptime(
            request.form['birthday'], "%Y-%m-%d").timestamp())
        success = updateUserDB(current_user.email, None, str(birthday),
                               request.form['firstName'], request.form['lastName'], request.form['genderRadio'], request.form['size'], request.form['weight'], None, None, None)

        if success:
            flash('Profil erflogreich gespeichert.')
            return redirect("/settings?alert=success")
        else:
            flash('Unbekannter Fehler beim Bearbeiten der Profilinformationen!')
            return redirect("/settings?alert=danger")
    else:
        return redirect("/login")

# Update user informations
@app.route("/changeProfileImg", methods=['POST'])
def changeProfileImg():
    if current_user.is_authenticated:
        image = request.form["base64Img"]
        success = updateUserDB(current_user.id, None, None,
                               None, None, None, None, None, image, None, None)

        if success:
            flash('Profilbild erfolgreich aktualisiert.')
            return redirect("/settings?alert=success")
        else:
            flash('Unbekannter Fehler beim Bearbeiten der Profilbildes!')
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
                flash('Passwort wurde erfolgreich geändert.')
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
        success = deleteUserById(current_user.id)

        if success == 0:
            flash('Ihr Account wurde erfolgreich gelöscht.')
            logout_user()
            return redirect("/login?alert=success")
        else:
            flash('Unbekannter Fehler beim Löschen des Accounts!')
            return redirect("/settings?alert=danger")
    else:
        return redirect("/login")

# Delete single record
@app.route("/deleteRecord", methods=['POST'])
def deleteRecord():
    if current_user.is_authenticated:
        success = deleteRecordById(request.form['recordId'])

        if success == 0:
            flash('Aufzeichnung erfolgreich gelöscht.')
            return redirect("/records?alert=success")
        else:
            flash('Unbekannter Fehler beim Löschen der Aufzeichnung!')
            return redirect("/records?alert=danger")
    else:
        return redirect("/login")

# Get image from user
@app.route("/image", methods=['GET'])
def getImage():
    try:
        userID = request.args.get('userID')

        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT '+app.config['DB_USERS_IMAGE']+' FROM '+app.config['DB_TABLE_USERS'] + ' WHERE '+app.config['DB_USERS_ID']+' = "' + userID + '";')
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

# Edit record name
@app.route("/editRecord", methods=['POST'])
def editRecord():
    if current_user.is_authenticated:
        success = updateRecordDB(
            request.form['recordId'], request.form['recordName'], str(int(time.time())))

        if success:
            flash('Die Aufzeichnung wurde erfolgreich editiert.')
            return redirect("/records?alert=success")
        else:
            flash('Unbekannter Fehler beim Editieren der Aufzeichnung!')
            return redirect("/records?alert=danger")
    else:
        return redirect("/login")

# Verify email after registration (over link)
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
    jsonObj['records'] = getRecordsByID(result[0], 0)
  #  jsonObj['locations'] = getLocationsByID(result[0], None)
    # TODO: Übertragung aller Locations des Nutzers
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
        jsonRequest['firstName'], jsonRequest['lastName'], jsonRequest['email'], jsonRequest['password'],  jsonRequest['dateOfBirth'],  jsonRequest['gender'])

    return json.dumps(jsonObj)

# Get all userdata with image by id
@app.route("/getUserByIdAPI", methods=['POST'])
@requires_authorization
def getUserByIdAPI():
    return json.dumps(getUserWithImageFromDB(request.json['id']))

# Get all Records by userId and Page
@app.route("/getRecordsByIdAPI", methods=['POST'])
@requires_authorization
def getRecordsByIdAPI():
    return json.dumps(getRecordsByID(request.json['id'], int(request.json['page'])))

# Edit record name
@app.route("/editRecordAPI", methods=['POST'])
def editRecordAPI():
    j = request.json

    jsonSuccess = {}
    if updateRecordDB(j['recordId'], j['recordName'], j['timestamp']):
        jsonSuccess['success'] = 0
    else:
        jsonSuccess['success'] = 1

    return json.dumps(jsonSuccess)

# Update user data in database
@app.route("/updateUserAPI", methods=['POST'])
@requires_authorization
def updateUserAPI():
    j = request.json

    jsonSuccess = {}

    auth = request.authorization

    # try email from json, if not possible get from auth
    try:
        email = auth.username
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


def saveTrackThread(jsonTrack):

    try:
       # jsonTrack = json.loads(jsonString)

        conn = mysql.connect()
        cursor = conn.cursor()

        print('INSERT INTO '+app.config['DB_TABLE_RECORDS'] +
              ' ('
              + app.config['DB_RECORD_NAME'] + ','
              + app.config['DB_RECORD_TIME'] + ','
              + app.config['DB_RECORD_DATE'] + ','
              + app.config['DB_RECORD_TYPE'] + ','
              + app.config['DB_RECORD_RIDETIME'] + ','
              + app.config['DB_RECORD_DISTANCE'] + ','
              + app.config['DB_RECORD_TIMESTAMP'] + ','
              + app.config['DB_RECORD_USERS_ID']+') VALUES ("'
              + jsonTrack['name'] + '", '
              + str(jsonTrack['time']) + ', '
              + str(jsonTrack['date']) + ', '
              + str(jsonTrack['type']) + ', '
              + str(jsonTrack['rideTime']) + ', '
              + str(jsonTrack['distance']) + ', '
              + str(jsonTrack['timeStamp']) + ', '
              + str(jsonTrack['userId']) + ');')

        cursor.execute(
            'INSERT INTO '+app.config['DB_TABLE_RECORDS'] +
            ' ('
            + app.config['DB_RECORD_NAME'] + ','
            + app.config['DB_RECORD_TIME'] + ','
            + app.config['DB_RECORD_DATE'] + ','
            + app.config['DB_RECORD_TYPE'] + ','
            + app.config['DB_RECORD_RIDETIME'] + ','
            + app.config['DB_RECORD_DISTANCE'] + ','
            + app.config['DB_RECORD_TIMESTAMP'] + ','
            + app.config['DB_RECORD_USERS_ID']+') VALUES ("'
            + jsonTrack['name'] + '", '
            + str(jsonTrack['time']) + ', '
            + str(jsonTrack['date']) + ', '
            + str(jsonTrack['type']) + ', '
            + str(jsonTrack['rideTime']) + ', '
            + str(jsonTrack['distance']) + ', '
            + str(jsonTrack['timeStamp']) + ', '
            + str(jsonTrack['userId']) + ');')

        routeId = cursor.lastrowid

        for jsonLocation in jsonTrack['locations']:
            cursor.execute(
                'INSERT INTO ' + app.config['DB_TABLE_LOCATIONS'] +
                ' ('
                + app.config['DB_LOCATION_LATITUDE'] + ','
                + app.config['DB_LOCATION_LONGITUDE'] + ','
                + app.config['DB_LOCATION_ALTITUDE'] + ','
                + app.config['DB_LOCATION_TIME'] + ','
                + app.config['DB_LOCATION_SPEED'] + ','
                + app.config['DB_LOCATION_RECORD_ID'] + ') VALUES ('
                + str(jsonLocation['latitude']) + ', '
                + str(jsonLocation['longitude']) + ', '
                + str(jsonLocation['altitude']) + ', '
                + str(jsonLocation['time']) + ', '
                + str(jsonLocation['speed']) + ', '
                + str(routeId) + ');')

        conn.commit()

        cursor.close()
        conn.close()

        pass
    except Exception as identifier:

        print(identifier)

        pass


@app.route("/uploadTrackAPI", methods=['POST'])
@requires_authorization
def uploadTrackAPI():
    jsonSuccess = {}

    try:
        jsonTrack = request.json
        thread = Thread(target=saveTrackThread, args=(jsonTrack,))
        thread.start()

        conn = mysql.connect()
        cursor = conn.cursor()

        sql = ('INSERT INTO ' + app.config['DB_TABLE_RECORDS'] + ' ('
               + app.config['DB_RECORD_NAME'] + ','
               + app.config['DB_RECORD_TIME'] + ','
               + app.config['DB_RECORD_DATE'] + ','
               + app.config['DB_RECORD_TYPE'] + ','
               + app.config['DB_RECORD_RIDETIME'] + ','
               + app.config['DB_RECORD_DISTANCE'] + ','
               + app.config['DB_RECORD_TIMESTAMP'] + ','
               + app.config['DB_RECORD_USERS_ID'] + ','
               + app.config['DB_RECORD_LOCATION_DATA'] + ') VALUES ("'
               + jsonTrack['name'] + '", '
               + str(jsonTrack['time']) + ', '
               + str(jsonTrack['date']) + ', '
               + str(jsonTrack['type']) + ', '
               + str(jsonTrack['rideTime']) + ', '
               + str(jsonTrack['distance']) + ', '
               + str(jsonTrack['timeStamp']) + ', '
               + str(jsonTrack['userId']) + ', %s);')

        for loc in jsonTrack['locations']:
            del loc[app.config['ANDROID_LOCATION_RECORD_ID']]

        cursor.execute(sql, (str(json.dumps(jsonTrack['locations'])),))

        conn.commit()

        conn.close()

        jsonSuccess['success'] = 0
        jsonSuccess['record'] = getSingleRecordByID(cursor.lastrowid)
        jsonSuccess['oldId'] = jsonTrack['id']
        cursor.close()
        pass
    except Exception as identifier:
        jsonSuccess['success'] = 1
        pass

    return json.dumps(jsonSuccess)


@app.route("/synchronizeRecordsAPI", methods=['POST'])
@requires_authorization
def synchronizeRecordsAPI():

    jarr = request.json

    conn = mysql.connect()
    cursor = conn.cursor()

    ids = []

    janswer = {}
    janswer['missingId'] = []
    janswer['onServer'] = []
    janswer['newerOnServer'] = []
    janswer['deletedOnServer'] = []

    for jsn in jarr:
        ids.append(int(jsn['id']))

        cursor.execute('SELECT ' + app.config['DB_RECORD_TIMESTAMP'] + ", " + app.config['DB_RECORD_NAME'] +
                       ' FROM '+app.config['DB_TABLE_RECORDS'] + ' WHERE '+app.config['DB_RECORD_ID']+' = "' + jsn['id'] + '";')
        result = cursor.fetchone()

        timeStamp = int(jsn['timeStamp'])

        if result == None:
            # record not in Server DB
            janswer['missingId'].append(jsn['id'])
        elif result[0] < timeStamp:
            # update Recordname
            sql = 'UPDATE ' + app.config['DB_TABLE_RECORDS'] + \
                ' SET  ' + app.config['DB_RECORD_NAME'] + " = %s;"
            cursor.execute(sql, (jsn['name'],))
            conn.commit()
        elif result[0] > timeStamp:
            jnewName = {}
            jnewName['id'] = jsn['id']
            jnewName['timeStamp'] = result[0]
            jnewName['name'] = result[1]

            janswer['newerOnServer'].append(jnewName)
            pass

    try:

        if len(ids) > 0:
            placeholders = ', '.join(['%s']*len(ids))  # "%s, %s, %s, ... %s"

            sql = "SELECT " + app.config['DB_RECORD_ID'] + " FROM " + app.config['DB_TABLE_RECORDS'] + \
                " WHERE " + app.config['DB_RECORD_ID'] + \
                " NOT IN ({});".format(placeholders)

            cursor.execute(sql, tuple(ids))

            result = cursor.fetchall()

        else:
            sql = "SELECT " + app.config['DB_RECORD_ID'] + \
                " FROM " + app.config['DB_TABLE_RECORDS'] + ";"

            cursor.execute(sql)

            result = cursor.fetchall()

        if result != None:
            for idres in result:
                janswer['onServer'].append(getSingleRecordByID(idres[0]))
            # append records to array
        pass
    except Exception as identifier:
        print(identifier)
        pass

    try:

        auth = request.authorization
        usrid = getUserId(auth.username)

        sql = ("SELECT " + app.config['DB_RECORD_ID'] + " FROM "
               + app.config['DB_TABLE_RECORDS'] + " WHERE "
               + app.config['DB_RECORD_USERS_ID'] + " = " + str(usrid) + ";"
               )

        cursor.execute(sql)

        idsInDB = []

        result = cursor.fetchall()

        for res in result:
            idsInDB.append(res[0])

        deletedIds = list(set(ids) - set(idsInDB))

        for delID in deletedIds:
            jid = {}
            jid['id'] = delID
            janswer['deletedOnServer'].append(jid)

        # if len(ids) > 0:
        #     placeholders = ', '.join(['%s']*len(ids))  # "%s, %s, %s, ... %s"
        #     sql = "SELECT " + app.config['DB_RECORD_ID'] + " FROM " + app.config['DB_TABLE_RECORDS'] + " WHERE " + app.config['DB_RECORD_ID'] + " IN ({});".format(placeholders)

        #     cursor.execute(sql, tuple(ids))

        #     result = cursor.fetchall()

        #     for res in result:
        #         jid={}
        #         jid['id'] = res[0]
        #         janswer['deletedOnServer'].append(jid)

        pass
    except Exception as identifier:
        print(identifier)
        pass

    cursor.close()
    conn.close()

    return json.dumps(janswer)


@app.route("/deleteRecordAPI", methods=['POST'])
@requires_authorization
def deleteRecordAPI():
    jrequest = request.json

    jsonAnswer = {}
    conn = mysql.connect()
    cursor = conn.cursor()
    try:
        auth = request.authorization
        usrid = getUserId(auth.username)

        sql = 'DELETE FROM ' + app.config['DB_TABLE_RECORDS'] + " WHERE " + app.config['DB_RECORD_ID'] + \
            " = " + jrequest['recordId'] + " AND " + \
            app.config['DB_RECORD_USERS_ID'] + " = " + str(usrid) + ";"

        cursor.execute(sql)
        conn.commit()
        jsonAnswer['success'] = 0
        pass
    except Exception as identifier:
        jsonAnswer['success'] = 1
        pass

    cursor.close()
    conn.close()
    return json.dumps(jsonAnswer)


@app.route("/searchFriendsAPI", methods=['POST'])
@requires_authorization
def searchFriendsAPI():
    jrequest = request.json

    page = int(jrequest['page'])
    search = jrequest['search']

    jsonArr = searchFriend(page, search, None)

    return json.dumps(jsonArr)


@app.route("/searchMyFriendsAPI", methods=['POST'])
@requires_authorization
def searchMyFriendsAPI():
    jrequest = request.json

    auth = request.authorization
    usrid = getUserId(auth.username)

    page = int(jrequest['page'])
    search = jrequest['search']

    jsonArr = searchFriend(page, search, usrid)

    return json.dumps(jsonArr)


def searchFriend(page, search, usrId):
    conn = mysql.connect()
    cursor = conn.cursor()

    jsonArr = []

    try:

        start = page * 10 - 10
        end = page * 10

        if page > 0:
            limitter = ' LIMIT ' + str(start) + ', ' + str(end)
        else:
            limitter = ''

        auth = request.authorization

        join = ""
        whereID = ""
        if usrId != None:
            join = (" INNER JOIN " + app.config['DB_TABLE_HAS_USERS'] + " ON "
                    + app.config['DB_TABLE_USERS'] +
                    "." + app.config['DB_USERS_ID']
                    + " = " + app.config['DB_TABLE_HAS_USERS'] +
                    "." + app.config['DB_USERS_HAS_USERS_ASKER']
                    + " OR " + app.config['DB_TABLE_USERS'] +
                    "." + app.config['DB_USERS_ID']
                    + " = " + app.config['DB_TABLE_HAS_USERS'] + "." + app.config['DB_USERS_HAS_USERS_ASKED'] + " ")

            whereID = " AND " + app.config['DB_USERS_ID'] + " = " + str(usrId) + " "

        sql = ('SELECT ' + app.config['DB_USERS_ID']
               + ", " + app.config['DB_USERS_FIRSTNAME']
               + ", " + app.config['DB_USERS_LASTNAME']
               + ", " + app.config['DB_USERS_IMAGE']
               + ", " + app.config['DB_USERS_DATEOFREGISTRATION']
               + " FROM " + app.config['DB_TABLE_USERS']
               + join
               + " WHERE UPPER(" + app.config['DB_USERS_FIRSTNAME'] +
               ") LIKE UPPER('" + search + "%') "
               + " OR UPPER(" + app.config['DB_USERS_LASTNAME'] +
               ") LIKE UPPER('" + search + "%') "
               + " OR UPPER(" + app.config['DB_USERS_EMAIL'] +
               ") LIKE UPPER('" + search + "%') "
               + " AND UPPER(" + app.config['DB_USERS_EMAIL'] +
               ") != UPPER('" + auth.username + "') "
               + whereID
               + limitter
               )

        cursor.execute(sql)

        result = cursor.fetchall()

        for res in result:
            jres = {}
            jres['id'] = res[0]
            jres['firstName'] = res[1]
            jres['lastName'] = res[2]
            jres['image'] = res[3]
            jres['dateOfRegistration'] = res[4]

            cursor.execute("SELECT " + app.config['DB_RECORD_DISTANCE'] + " FROM " +
                           app.config['DB_TABLE_RECORDS'] + " WHERE users_id = " + str(res[0]) + ";")

            resultDist = cursor.fetchall()

            totDist = 0
            for record in resultDist:
                totDist += record[0]

            jres['totalDistance'] = totDist

            jsonArr.append(jres)

        pass
    except Exception as identifier:

        pass

    cursor.close()
    conn.close()

    return jsonArr


@app.route("/requestFriendAPI", methods=['POST'])
@requires_authorization
def requestFriendAPI():
    jrequest = request.json

    friendId = int(jrequest['friendId'])

    auth = request.authorization
    usrid = getUserId(auth.username)

    conn = mysql.connect()
    cursor = conn.cursor()

    janswer = {}

    try:

        sql = ("SELECT * FROM " + app.config['DB_TABLE_HAS_USERS']
               + " WHERE " + app.config['DB_USERS_HAS_USERS_ASKER'] + " = "
               + str(friendId) + " AND "
               + app.config['DB_USERS_HAS_USERS_ASKED'] + " = "
               + str(usrid) + " AND "
               + app.config['DB_USERS_HAS_USERS_AF'] + " = 0;"
               )

        cursor.execute(sql)

        result = cursor.fetchone()

        if result != None:
            sql = ("UPDATE " + app.config['DB_TABLE_HAS_USERS']
                   + " SET " + app.config['DB_USERS_HAS_USERS_AF'] + " = 1, "
                   + app.config['DB_USERS_HAS_USERS_DOF']
                   + " = " + str(int(time.time()))
                   + " WHERE " + app.config['DB_USERS_HAS_USERS_ASKER'] + " = "
                   + str(friendId) + " AND "
                   + app.config['DB_USERS_HAS_USERS_ASKED'] + " = "
                   + str(usrid) + " AND "
                   + app.config['DB_USERS_HAS_USERS_AF'] + " = 0;"
                   )
            janswer['success'] = 2

        else:
            sql = ("INSERT INTO " + app.config['DB_TABLE_HAS_USERS'] + " ("
                   + app.config['DB_USERS_HAS_USERS_ASKER'] + ", "
                   + app.config['DB_USERS_HAS_USERS_ASKED'] + ") VALUES ("
                   + str(usrid) + ", " + str(friendId) + ");")

            janswer['success'] = 0

        cursor.execute(sql)

        conn.commit()

        pass
    except Exception as identifier:
        janswer['success'] = 1

        pass
    cursor.close()
    conn.close()

    return json.dumps(janswer)


@app.route("/showFriendRequestAPI", methods=['POST'])
@requires_authorization
def showFriendRequestAPI():

    auth = request.authorization
    usrid = getUserId(auth.username)

    janswerArr = []

    conn = mysql.connect()
    cursor = conn.cursor()

    try:
        sql = ("SELECT " + app.config['DB_USERS_HAS_USERS_ASKER']
               + " FROM " + app.config['DB_TABLE_HAS_USERS']
               + " WHERE "
               + app.config['DB_USERS_HAS_USERS_ASKED']
               + " = " + str(usrid) + " AND "
               + app.config['DB_USERS_HAS_USERS_AF'] + " = 0;")

        cursor.execute(sql)

        result = cursor.fetchall()

        for res in result:
            janswerArr.append(getFriendById(res[0]))
    except Exception as identifier:
        pass

    cursor.close()
    conn.close()

    return json.dumps(janswerArr)


def getFriendById(firendId):
    conn = mysql.connect()
    cursor = conn.cursor()

    jres = {}

    try:
        sql = ('SELECT ' + app.config['DB_USERS_FIRSTNAME']
               + ", " + app.config['DB_USERS_LASTNAME']
               + ", " + app.config['DB_USERS_IMAGE']
               + ", " + app.config['DB_USERS_DATEOFREGISTRATION']
               + " FROM " + app.config['DB_TABLE_USERS']
               + " WHERE " + app.config['DB_USERS_ID'] + " = "
               + str(firendId) + ";"
               )

        cursor.execute(sql)

        res = cursor.fetchone()

        jres = {}
        jres['id'] = firendId
        jres['firstName'] = res[0]
        jres['lastName'] = res[1]
        jres['image'] = res[2]
        jres['dateOfRegistration'] = res[3]
        jres['totalDistance'] = getUserTotalDistance(firendId)
        pass
    except Exception as identifier:
        pass
    cursor.close()
    conn.close()

    return jres


def getUserTotalDistance(usrId):
    conn = mysql.connect()
    cursor = conn.cursor()

    totDist = 0
    try:

        cursor.execute("SELECT " + app.config['DB_RECORD_DISTANCE'] + " FROM " +
                       app.config['DB_TABLE_RECORDS'] + " WHERE users_id = " + str(usrId) + ";")

        resultDist = cursor.fetchall()

        for record in resultDist:
            totDist += record[0]
        pass
    except Exception as identifier:
        pass

    cursor.close()
    conn.close()

    return totDist


@app.route("/showStrangerProfileAPI", methods=['POST'])
@requires_authorization
def showStrangerProfileAPI():
    jrequest = request.json

    strangerId = int(jrequest['strangerId'])

    conn = mysql.connect()
    cursor = conn.cursor()

    jres = {}

    try:
        jres = getFriendById(strangerId)

        sql = ("SELECT " + app.config['DB_USERS_GENDER'] + ", "
               + app.config['DB_USERS_DATEOFBIRTH'] + " FROM "
               + app.config['DB_TABLE_USERS'] + " WHERE "
               + app.config['DB_USERS_ID'] + " = "
               + str(strangerId) + ";")

        cursor.execute(sql)

        result = cursor.fetchone()

        jres['gender'] = result[0]
        jres['dateOfBirth'] = result[1]
        pass
    except Exception as identifier:
        pass

    cursor.close()
    conn.close()

    return json.dumps(jres)


@app.route("/showFriendProfileAPI", methods=['POST'])
@requires_authorization
def showFriendProfileAPI():
    jrequest = request.json

    auth = request.authorization
    usrid = getUserId(auth.username)

    friendId = int(jrequest['friendId'])

    friend = showFriendProfile(friendId, usrid)

    return json.dumps(friend)


def showFriendProfile(friendID, userId):
    janswer = {}

    conn = mysql.connect()
    cursor = conn.cursor()

    try:

        sql = ("SELECT " + app.config['DB_USERS_HAS_USERS_AF'] + " FROM "
               + app.config['DB_TABLE_HAS_USERS'] + " WHERE "
               + app.config['DB_USERS_HAS_USERS_ASKER'] +
               " IN (" + str(friendID) + ", " + str(userId) + ")"
               + " AND " + app.config['DB_USERS_HAS_USERS_ASKED'] + " IN ("
               + str(friendID) + ", " + str(userId) + ");")

        cursor.execute(sql)

        result = cursor.fetchone()

        if result != None:
            janswer = getUserWithImageFromDB(friendID)

            del janswer['password']
            del janswer['weight']
            del janswer['size']
            del janswer['hints']
            del janswer['darkTheme']
            del janswer['timeStamp']

        pass
    except Exception as identifier:
        pass
    return janswer


###########################
###     Flask start     ###
###########################
if __name__ == '__main__':
    app.run(host='0.0.0.0')
