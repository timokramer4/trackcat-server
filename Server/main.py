###########################
###       Imports       ###
###########################

from flask import Flask, flash, request, render_template, redirect, jsonify, session, make_response, send_file
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user
from dateutil.relativedelta import relativedelta
from mailSend import sendVmail, sendResetMail
from datetime import datetime, timedelta
from passlib.hash import pbkdf2_sha256
from flaskext.mysql import MySQL
from threading import Thread
from functools import wraps

import simplejson
import time
import os
import json
import math
import base64
import io
import random
import hashlib
import calendar


###########################
###    Configuration    ###
###########################

app = Flask(__name__)
mysql = MySQL()
app.config['SESSION_LIFETIME'] = False

app.secret_key = "TOLLERSECRETKEY"  # TODO generate Secret key
app.config['MYSQL_DATABASE_USER'] = 'remRoot'
app.config['MYSQL_DATABASE_PASSWORD'] = '1Qayse45&'
app.config['MYSQL_DATABASE_DB'] = 'TrackCatDB'
app.config['MYSQL_DATABASE_HOST'] = 'safe-harbour.de'
app.config['MYSQL_DATABASE_PORT'] = 42042
mysql.init_app(app)

app.config['BASE_URL'] = "http://safe-harbour.de:4242"
#app.config['BASE_URL'] = "http://192.168.178.46:5000"


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
app.config['DB_USERS_RESETTOKEN'] = "resetToken"

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

# COLUMN-NAMES: Live-Record
app.config['DB_LIVE_RECORD_ID'] = 'id'
app.config['DB_LIVE_RECORD_TIME'] = 'time'
app.config['DB_LIVE_RECORD_TYPE'] = 'type'
app.config['DB_LIVE_RECORD_RIDETIME'] = 'rideTime'
app.config['DB_LIVE_RECORD_DISTANCE'] = 'distance'
app.config['DB_LIVE_RECORD_USERS_ID_FK'] = 'users_id'


# COLUMN-NAMES: Location
app.config['DB_LOCATION_ID'] = 'id'
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

# Refresh session timeout every reload
@app.before_request
def before_request():
    if app.config['SESSION_LIFETIME'] == True:
        session.permanent = True
        app.permanent_session_lifetime = timedelta(days=7)
    else:
        session.permanent = False
        app.permanent_session_lifetime = timedelta(seconds=5)

# Clear cache after request
@app.after_request
def add_header(response):
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response

# Format time
@app.template_filter('formatSeconds')
def formatSeconds(value):
    return str(timedelta(seconds=value))

# Format date
@app.template_filter('formatDate')
def formatDate(value, format='%d.%m.%Y %H:%M:%S'):
    return (datetime(1970, 1, 1) + timedelta(seconds=(value/1000))).strftime(format)

# Validate login data
@login_manager.user_loader
def user_loaderlmgr(id):
    conn = mysql.connect()
    cursor = conn.cursor()

    sql = ('SELECT ' + app.config['DB_USERS_ID']
           + ' FROM '+app.config['DB_TABLE_USERS'] + ' WHERE '
           + app.config['DB_USERS_ID']+' = %s;')

    cursor.execute(sql, (id,))
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

    sql = ('SELECT ' + app.config['DB_USERS_ID']
           + ' FROM '+app.config['DB_TABLE_USERS'] + ' WHERE '
           + app.config['DB_USERS_EMAIL']+' = %s;')

    cursor.execute(sql, (email,))
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

    sql = ('SELECT ' + app.config['DB_USERS_PASSWORD']
           + ' FROM '+app.config['DB_TABLE_USERS']
           + ' WHERE ' + app.config['DB_USERS_EMAIL']
           + ' = %s;')

    cursor.execute(sql, (email,))

    result = cursor.fetchone()
    cursor.close()
    conn.close()

    return result is not None and pbkdf2_sha256.verify(password, result[0])


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

        token = generateVerifyToken(firstName, lastName, email)

        sql = ('INSERT INTO '+app.config['DB_TABLE_USERS'] + ' ('
               + app.config['DB_USERS_FIRSTNAME']+', '
               + app.config['DB_USERS_LASTNAME']+', '
               + app.config['DB_USERS_EMAIL']+', '
               + app.config['DB_USERS_PASSWORD']+', '
               + app.config['DB_USERS_DATEOFBIRTH']+', '
               + app.config['DB_USERS_GENDER']+', '
               + app.config['DB_USERS_DATEOFREGISTRATION']+', '
               + app.config['DB_USERS_LASTLOGIN']+', '
               + app.config['DB_USERS_DARKTHEME']+', '
               + app.config['DB_USERS_HINTS']+', '
               + app.config['DB_USERS_TIMESTAMP']+', '
               + app.config['DB_USERS_VERIFYTOKEN']+') VALUES (%s,%s,%s,%s,%s,%s,%s,%s, 0, 1,%s,%s);')

        cursor.execute(sql, (firstName, lastName, email, pbkdf2_sha256.hash(password), birthday, gender, str(
            int(time.time())), str(int(time.time())), str(int(time.time())), token,))

        conn.commit()

        sendVmail(email, firstName,  baseUrl + token)
        success = 0

    except Exception as identifier:
        print(identifier)

        if(identifier.args[0] == 1062):
            if('eMail_UNIQUE' in identifier.args[1]):
                success = 3
        else:
            success = 1
    pass
    cursor.close()
    conn.close()

    return success


# sha256 hash password
def hash256Password(password):
    hash_object = hashlib.sha256(str.encode(password))

    return hash_object.hexdigest()


# Generate verify token
def generateVerifyToken(firstName, lastName, email):

    userData = [firstName, lastName, email]

    random.shuffle(userData)
    token = pbkdf2_sha256.hash(userData[0]+userData[1]+userData[2])

    return token


# Get selected user data as JSON
def getUserFromDB(id):
    conn = mysql.connect()
    cursor = conn.cursor()
    params = (app.config['DB_USERS_ID']+', '
              + app.config['DB_USERS_EMAIL']+', '
              + app.config['DB_USERS_FIRSTNAME']+', '
              + app.config['DB_USERS_LASTNAME']+', '
              + app.config['DB_USERS_DATEOFBIRTH']+', '
              + app.config['DB_USERS_GENDER']+', '
              + app.config['DB_USERS_WEIGHT']+', '
              + app.config['DB_USERS_SIZE']+', '
              + app.config['DB_USERS_DARKTHEME']+', '
              + app.config['DB_USERS_HINTS'] + ', '
              + app.config['DB_USERS_DATEOFREGISTRATION']+', '
              + app.config['DB_USERS_LASTLOGIN']+', '
              + app.config['DB_USERS_TIMESTAMP'])

    sql = ('SELECT ' + params
           + ' FROM '+app.config['DB_TABLE_USERS'] + ' WHERE '
           + app.config['DB_USERS_ID']+' = %s;')

    cursor.execute(sql, (id,))
    result = cursor.fetchone()

    jsonUser = {}
    jsonUser['id'] = result[0]
    jsonUser['email'] = result[1]
    jsonUser['firstName'] = result[2]
    jsonUser['lastName'] = result[3]
    jsonUser['dateOfBirth'] = result[4]
    if result[5] == None:
        jsonUser['gender'] = 2
    else:
        jsonUser['gender'] = result[5]
    jsonUser['weight'] = result[6]
    jsonUser['size'] = result[7]
    jsonUser['darkTheme'] = result[8]
    jsonUser['hints'] = result[9]
    jsonUser['dateOfRegistration'] = result[10]
    jsonUser['lastLogin'] = result[11]
    jsonUser['timeStamp'] = result[12]

    # not saved statistics total ridetime amout of records and total distance

    sql = ("SELECT " + app.config['DB_RECORD_DISTANCE'] + ", "
           + app.config['DB_RECORD_RIDETIME']
           + " FROM " + app.config['DB_TABLE_RECORDS']
           + " WHERE users_id = %s;")

    cursor.execute(sql, (result[0],))

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

    sql = ('SELECT '+app.config['DB_USERS_IMAGE']+' FROM '
           + app.config['DB_TABLE_USERS']
           + ' WHERE '+app.config['DB_USERS_ID']+' = %s;')

    cursor.execute(sql, (id,))
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

        sql = ('UPDATE ' + app.config['DB_TABLE_USERS']+' SET '
               + app.config['DB_USERS_LASTLOGIN']+' = %s WHERE '
               + app.config['DB_USERS_EMAIL']+' = %s;')

        cursor.execute(sql, (int(time.time()), email,))

        conn.commit()

        conn.close()
        pass
    except Exception as identifier:
        pass
    return


# Update user informations in database
def updateUserDB(userId, dateOfBirth, firstName, lastName,
                 gender, size, weight, image, timestamp, hints, darkTheme):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()

        if dateOfBirth is not None:
            sql = ('UPDATE '+app.config['DB_TABLE_USERS'] + ' SET '
                   + app.config['DB_USERS_DATEOFBIRTH']+' =  %s WHERE '
                   + app.config['DB_USERS_ID']+' = %s;')

            cursor.execute(sql, (dateOfBirth, userId,))

        if firstName is not None:
            sql = ('UPDATE '+app.config['DB_TABLE_USERS'] + ' SET '
                   + app.config['DB_USERS_FIRSTNAME']+' = %s WHERE '
                   + app.config['DB_USERS_ID']+' = %s;')

            cursor.execute(sql, (firstName, userId,))

        if lastName is not None:
            sql = ('UPDATE '+app.config['DB_TABLE_USERS'] + ' SET  '
                   + app.config['DB_USERS_LASTNAME']+' = %s WHERE '
                   + app.config['DB_USERS_ID']+' = %s;')

            cursor.execute(sql, (lastName, userId,))

        if gender is not None:
            sql = ('UPDATE '+app.config['DB_TABLE_USERS'] + ' SET '
                   + app.config['DB_USERS_GENDER']+' = %s WHERE '
                   + app.config['DB_USERS_ID']+' = %s;')

            cursor.execute(sql, (gender, userId,))

        if size is not None:
            sql = ('UPDATE '+app.config['DB_TABLE_USERS'] + ' SET '
                   + app.config['DB_USERS_SIZE']+' = %s WHERE '
                   + app.config['DB_USERS_ID']+' = %s;')

            cursor.execute(sql, (size, userId,))

        if weight is not None:
            sql = ('UPDATE '+app.config['DB_TABLE_USERS'] + ' SET  '
                   + app.config['DB_USERS_WEIGHT']+' = %s WHERE '
                   + app.config['DB_USERS_ID']+' = %s;')

            cursor.execute(sql, (weight, userId,))

        if image is not None:
            sql = ('UPDATE '+app.config['DB_TABLE_USERS'] + ' SET '
                   + app.config['DB_USERS_IMAGE']+' = %s WHERE '
                   + app.config['DB_USERS_ID']+' = %s;')

            cursor.execute(sql, (image, userId,))

        if hints is not None:
            sql = ('UPDATE '+app.config['DB_TABLE_USERS'] + ' SET '
                   + app.config['DB_USERS_HINTS']+' = %s WHERE '
                   + app.config['DB_USERS_ID']+' = %s;')

            cursor.execute(sql, (hints, userId,))

        if darkTheme is not None:
            sql = ('UPDATE '+app.config['DB_TABLE_USERS'] + ' SET '
                   + app.config['DB_USERS_DARKTHEME']+' = %s WHERE '
                   + app.config['DB_USERS_ID']+' = %s;')

            cursor.execute(sql, (darkTheme, userId,))

        if timestamp is not None:
            sql = ('UPDATE '+app.config['DB_TABLE_USERS'] + ' SET '
                   + app.config['DB_USERS_TIMESTAMP']+' = %s WHERE '
                   + app.config['DB_USERS_ID']+' = %s;')

            cursor.execute(sql, (timestamp, userId,))

        conn.commit()

        conn.close()
        pass
        return True
    except Exception as identifier:
        print(identifier)
        return False
        pass


# gets user id by email
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
def changeUserPasswordDB(id, password, newPw, timeStamp):
    result = 0
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        params = app.config['DB_USERS_PASSWORD']

        sql = ('SELECT ' + params
               + ' FROM '+app.config['DB_TABLE_USERS'] + ' WHERE '
               + app.config['DB_USERS_ID']+' = %s;')

        cursor.execute(sql, (id,))
        result = cursor.fetchone()

        if pbkdf2_sha256.verify(password, result[0]):

            sql = ('UPDATE '+app.config['DB_TABLE_USERS'] + ' SET '
                   + app.config['DB_USERS_PASSWORD']+' = %s, '
                   + app.config['DB_USERS_TIMESTAMP']+' = %s WHERE '
                   + app.config['DB_USERS_ID']+' = %s;')

            cursor.execute(sql, (pbkdf2_sha256.hash(newPw), timeStamp, id,))
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

        sql = ('DELETE FROM ' + app.config['DB_TABLE_USERS']
               + ' WHERE '+app.config['DB_USERS_ID']
               + ' = %s;')

        cursor.execute(sql, (id,))

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
            sql = ('UPDATE ' + app.config['DB_TABLE_RECORDS'] + ' SET '
                   + app.config['DB_RECORD_NAME'] + ' = %s, '
                   + app.config['DB_RECORD_TIMESTAMP'] + ' = %s WHERE '
                   + app.config['DB_RECORD_ID']+' = %s;')

            cursor.execute(sql, (newName, timestamp, recordId,))
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


# Delete record by id
def deleteRecordById(id):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()

        sql = ('DELETE FROM ' + app.config['DB_TABLE_RECORDS']
               + ' WHERE ' + app.config['DB_RECORD_ID']+' = %s;')

        cursor.execute(sql, (id,))

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

    params = (app.config['DB_RECORD_ID'] + ', '
              + app.config['DB_RECORD_NAME'] + ', '
              + app.config['DB_RECORD_TIME'] + ', '
              + app.config['DB_RECORD_DATE'] + ', '
              + app.config['DB_RECORD_TYPE'] + ', '
              + app.config['DB_RECORD_RIDETIME'] + ', '
              + app.config['DB_RECORD_DISTANCE'] + ', '
              + app.config['DB_RECORD_TIMESTAMP'] + ', '
              + app.config['DB_RECORD_LOCATION_DATA'])

    sql = ('SELECT ' + params + ' FROM '
           + app.config['DB_TABLE_RECORDS'] + ' WHERE '
           + app.config['DB_RECORD_USERS_ID'] + ' = %s' + limitter + ";")

    cursor.execute(sql, (userId,))
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


# Get amount of records
def getRecordsAmount(userId):
    conn = mysql.connect()
    cursor = conn.cursor()

    sql = ('SELECT count(*) FROM '
           + app.config['DB_TABLE_RECORDS'] + ' WHERE '
           + app.config['DB_RECORD_USERS_ID'] + ' = % s')

    cursor.execute(sql, (userId,))
    result = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return result


# get total Record time
def getTotalRecordTime(userId):
    conn = mysql.connect()
    cursor = conn.cursor()

    sql = ('SELECT ' + app.config['DB_RECORD_RIDETIME']
           + ' FROM ' + app.config['DB_TABLE_RECORDS']
           + ' WHERE ' + app.config['DB_RECORD_USERS_ID']
           + ' = %s;')

    cursor.execute(sql, (userId,))

    result = cursor.fetchall()

    rideTimeAmount = 0

    for res in result:
        rideTimeAmount += res[0]

    cursor.close()
    conn.close()

    return rideTimeAmount


# get total Record time
def getTotalPauseTime(userId):
    conn = mysql.connect()
    cursor = conn.cursor()

    sql = ('SELECT ' + app.config['DB_RECORD_TIME']
           + ', ' + app.config['DB_RECORD_RIDETIME']
           + ' FROM ' + app.config['DB_TABLE_RECORDS']
           + ' WHERE ' + app.config['DB_RECORD_USERS_ID']
           + ' = %s;')

    cursor.execute(sql, (userId,))

    result = cursor.fetchall()

    rideTimeAmount = 0

    for res in result:
        rideTimeAmount += (res[0]-res[1])

    cursor.close()
    conn.close()

    return rideTimeAmount


# Get friends amount
def getFriendsAmount(userId):
    conn = mysql.connect()
    cursor = conn.cursor()

    sql = ('SELECT count(*) FROM '
           + app.config['DB_TABLE_HAS_USERS'] + ' WHERE '
           + app.config['DB_USERS_HAS_USERS_ASKER'] + ' = %s OR '
           + app.config['DB_USERS_HAS_USERS_ASKED']
           + ' = %s;')

    cursor.execute(sql, (userId, userId,))
    result = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return math.ceil(result/10)


# Get single record by id
def getSingleRecordByID(recordId):
    conn = mysql.connect()
    cursor = conn.cursor()

    params = (app.config['DB_RECORD_ID'] + ', '
              + app.config['DB_RECORD_NAME'] + ', '
              + app.config['DB_RECORD_TIME'] + ', '
              + app.config['DB_RECORD_DATE'] + ', '
              + app.config['DB_RECORD_TYPE'] + ', '
              + app.config['DB_RECORD_RIDETIME'] + ', '
              + app.config['DB_RECORD_DISTANCE'] + ', '
              + app.config['DB_RECORD_TIMESTAMP'] + ', '
              + app.config['DB_RECORD_USERS_ID'] + ', '
              + app.config['DB_RECORD_LOCATION_DATA'])

    sql = ('SELECT ' + params + ' FROM '
           + app.config['DB_TABLE_RECORDS'] + ' WHERE '
           + app.config['DB_RECORD_ID'] + ' = %s;')

    cursor.execute(sql, (recordId,))
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
    jsonRecord['locations'] = res[9]

    return jsonRecord


# UNUSED maybe usefull in future TODO remove maybe
# Get all locations from user (and from specific route)
# def getLocationsByID(userId, recordId):
#     conn = mysql.connect()
#     cursor = conn.cursor()

#     if recordId is not None:
#         selection = app.config['DB_TABLE_RECORDS'] + '.' + \
#             app.config['DB_RECORD_ID'] + ' = ' + str(recordId)
#     else:
#         selection = app.config['DB_TABLE_RECORDS'] + '.' + \
#             app.config['DB_RECORD_USERS_ID'] + ' = ' + str(userId)

#     params = app.config['DB_LOCATION_LATITUDE'] + ', ' + app.config['DB_LOCATION_LONGITUDE'] + ', ' + app.config['DB_LOCATION_ALTITUDE'] + ', ' + \
#         app.config['DB_TABLE_LOCATIONS'] + '.' + app.config['DB_LOCATION_TIME'] + ', ' + \
#         app.config['DB_LOCATION_SPEED'] + ', ' + \
#         app.config['DB_LOCATION_RECORD_ID']
#     cursor.execute('SELECT ' + params + ' FROM ' + app.config['DB_TABLE_LOCATIONS'] + ' INNER JOIN ' + app.config['DB_TABLE_RECORDS'] + ' ON ' + app.config['DB_TABLE_LOCATIONS'] +
#                    '.' + app.config['DB_LOCATION_RECORD_ID'] + ' = ' + app.config['DB_TABLE_RECORDS'] + '.' + app.config['DB_RECORD_ID'] + ' AND ' + selection + ';')
#     result = cursor.fetchall()

#     cursor.close()
#     conn.close()

#     jsonLocations = []

#     for res in result:
#         jsonLocation = {}
#         jsonLocation['lat'] = res[0]
#         jsonLocation['lng'] = res[1]
#         jsonLocation['altitude'] = res[2]
#         jsonLocation['time'] = res[3]
#         jsonLocation['speed'] = res[4]
#         jsonLocation['record_id'] = res[5]

#         jsonLocations.append(jsonLocation)

#     return jsonLocations


# deletes Friendship or Request
def deleteFriend(friendId, usrId):
    conn = mysql.connect()
    cursor = conn.cursor()

    try:
        sql = ("DELETE FROM " + app.config['DB_TABLE_HAS_USERS']
               + " WHERE "
               + app.config['DB_USERS_HAS_USERS_ASKER']
               + " IN (%s, %s)" + " AND "
               + app.config['DB_USERS_HAS_USERS_ASKED'] + " IN (%s, %s);")

        cursor.execute(sql, (friendId, usrId, friendId, usrId,))
        conn.commit()

        success = 0

        pass
    except Exception as identifier:
        success = 1
        pass

    cursor.close()
    conn.close()

    return success


# TODO
def showFriendProfile(friendID, userId):
    janswer = {}

    conn = mysql.connect()
    cursor = conn.cursor()

    try:
        sql = ("SELECT " + app.config['DB_USERS_HAS_USERS_DOF'] + " FROM "
               + app.config['DB_TABLE_HAS_USERS'] + " WHERE "
               + app.config['DB_USERS_HAS_USERS_ASKER']
               + " IN (%s, %s)" + " AND "
               + app.config['DB_USERS_HAS_USERS_ASKED'] + " IN (%s,%s) AND "
               + app.config['DB_USERS_HAS_USERS_AF'] + " = 1;")

        cursor.execute(sql, (friendID, userId, friendID, userId,))

        result = cursor.fetchone()

        if result != None:
            janswer = getUserWithImageFromDB(friendID)

            del janswer['weight']
            del janswer['size']
            del janswer['hints']
            del janswer['darkTheme']
            del janswer['timeStamp']
            janswer['dateOfFriendship'] = result[0]
            janswer['areFriends'] = True

        else:
            janswer = getFriendById(friendID)

            del janswer['email']
            del janswer['totalDistance']

            sql = ("SELECT " + app.config['DB_USERS_DATEOFBIRTH']
                   + " FROM "
                   + app.config['DB_TABLE_USERS'] + " WHERE "
                   + app.config['DB_USERS_ID'] + " = %s;")

            cursor.execute(sql, (friendID,))

            result = cursor.fetchone()

            janswer['age'] = relativedelta(datetime.fromtimestamp(time.time()), datetime.fromtimestamp(result[0])).years

            janswer['areFriends'] = False
        pass
    except Exception as identifier:
        pass

    cursor.close()
    conn.close()
    return janswer


# calculates total distance by userID
def getUserTotalDistance(usrId):
    conn = mysql.connect()
    cursor = conn.cursor()

    totDist = 0
    try:
        sql = ("SELECT " + app.config['DB_RECORD_DISTANCE'] + " FROM "
               + app.config['DB_TABLE_RECORDS']
               + " WHERE users_id = %s;")

        cursor.execute(sql, (usrId,))

        resultDist = cursor.fetchall()

        for record in resultDist:
            totDist += record[0]
        pass
    except Exception as identifier:
        pass

    cursor.close()
    conn.close()

    return totDist


# TODO
def getFriendById(friendId):
    conn = mysql.connect()
    cursor = conn.cursor()

    jres = {}

    try:
        sql = ('SELECT ' + app.config['DB_USERS_FIRSTNAME']
               + ", " + app.config['DB_USERS_LASTNAME']
               + ", " + app.config['DB_USERS_EMAIL']
               + ", " + app.config['DB_USERS_IMAGE']
               + ", " + app.config['DB_USERS_DATEOFREGISTRATION']
               + " FROM " + app.config['DB_TABLE_USERS']
               + " WHERE " + app.config['DB_USERS_ID'] + " = %s;")

        cursor.execute(sql, (friendId,))

        res = cursor.fetchone()

        jres = {}
        jres['id'] = friendId
        jres['firstName'] = res[0]
        jres['lastName'] = res[1]
        jres['email'] = res[2]
        jres['image'] = res[3]
        jres['dateOfRegistration'] = res[4]
        jres['totalDistance'] = getUserTotalDistance(friendId)
        pass
    except Exception as identifier:
        pass
    cursor.close()
    conn.close()

    return jres


# list friend by parameters
# if usrId is Null serach for new Friends
# else search in friends
def searchFriends(page, search, usrId, usrEmail):
    conn = mysql.connect()
    cursor = conn.cursor()

    jsonArr = []

    try:
        start = page * 10 - 10
        end = page * 10

        if page > 0:
            limitter = ' LIMIT ' + str(start) + ', ' + str(10)
        else:
            limitter = ''

        join = ""
        whereID = ""
        email = ""
        case = ""
        group = ""

        isFriend = False

        if usrId != None:
            isFriend = True

            join = (" LEFT JOIN " + app.config['DB_TABLE_HAS_USERS'] + " ON "
                    + app.config['DB_TABLE_USERS'] +
                    "." + app.config['DB_USERS_ID']
                    + " = " + app.config['DB_TABLE_HAS_USERS'] +
                    "." + app.config['DB_USERS_HAS_USERS_ASKER']
                    + " OR " + app.config['DB_TABLE_USERS'] +
                    "." + app.config['DB_USERS_ID']
                    + " = " + app.config['DB_TABLE_HAS_USERS'] +
                    "." + app.config['DB_USERS_HAS_USERS_ASKED']
                    + " LEFT JOIN " +
                    app.config['DB_TABLE_LIVE_RECORDS'] + " ON "
                    + app.config['DB_TABLE_LIVE_RECORDS'] + "." +
                    app.config['DB_LIVE_RECORD_USERS_ID_FK']
                    + " = " + app.config['DB_TABLE_USERS'] + "." + app.config['DB_USERS_ID'])

            whereID = (app.config['DB_TABLE_USERS'] + "." + app.config['DB_USERS_ID'] + " != " + str(usrId) + " AND "
                       + app.config['DB_USERS_HAS_USERS_AF'] + " = 1 AND ("
                       + app.config['DB_TABLE_HAS_USERS'] + "." +
                       app.config['DB_USERS_HAS_USERS_ASKER']
                       + " = " + str(usrId) + " OR "
                       + app.config['DB_TABLE_HAS_USERS'] + "." +
                       app.config['DB_USERS_HAS_USERS_ASKED']
                       + " = " + str(usrId) + ") AND")
            email = (", " + app.config['DB_USERS_EMAIL'] + ", "
                     " CASE WHEN " + app.config['DB_TABLE_LIVE_RECORDS'] + "."
                     + app.config['DB_LIVE_RECORD_USERS_ID_FK'] + " > 0 THEN 1 ELSE 0 END AS isLive")
        else:

            usrId = getUserId(usrEmail)

            case = (", SUM((CASE WHEN (" + app.config['DB_TABLE_HAS_USERS']
                    + "." +
                    app.config['DB_USERS_HAS_USERS_ASKER'] +
                    " != " + str(usrId)
                    + " AND " + app.config['DB_TABLE_HAS_USERS']
                    + "." +
                    app.config['DB_USERS_HAS_USERS_ASKED'] +
                    " != " + str(usrId)
                    + ") OR (" + app.config['DB_TABLE_HAS_USERS']
                    + "." +
                    app.config['DB_USERS_HAS_USERS_ASKER'] + " is null AND "
                    + app.config['DB_TABLE_HAS_USERS']
                    + "." +
                    app.config['DB_USERS_HAS_USERS_ASKED'] + " is null)"
                    + " THEN 0 ELSE 1 END) ) AS tempSum"


                    )
            join = (" LEFT JOIN " + app.config['DB_TABLE_HAS_USERS'] + " ON ("
                    + app.config['DB_TABLE_USERS'] +
                    "." + app.config['DB_USERS_ID']
                    + " = " + app.config['DB_TABLE_HAS_USERS'] +
                    "." + app.config['DB_USERS_HAS_USERS_ASKER']
                        + " OR " + app.config['DB_TABLE_USERS'] +
                    "." + app.config['DB_USERS_ID']
                        + " = " + app.config['DB_TABLE_HAS_USERS'] + "." + app.config['DB_USERS_HAS_USERS_ASKED'] + ") ")

            group = (" GROUP BY " + app.config['DB_TABLE_USERS']
                     + "." + app.config['DB_USERS_ID']
                       + " HAVING tempSum = 0"
                     )

        sql = ('SELECT ' + app.config['DB_TABLE_USERS'] + "." + app.config['DB_USERS_ID']
               + ", " + app.config['DB_USERS_FIRSTNAME']
               + ", " + app.config['DB_USERS_LASTNAME']
               + ", " + app.config['DB_USERS_IMAGE']
               + ", " + app.config['DB_USERS_DATEOFREGISTRATION']
               + email
               + case
               + " FROM " + app.config['DB_TABLE_USERS']
               + join
               + " WHERE "
               + whereID
               + "(UPPER(" + app.config['DB_USERS_FIRSTNAME'] +
               ") LIKE UPPER('" + search + "%') "
               + " OR UPPER(" + app.config['DB_USERS_LASTNAME'] +
               ") LIKE UPPER('" + search + "%') "
               + " OR UPPER(" + app.config['DB_USERS_EMAIL'] +
               ") LIKE UPPER('" + search + "%')) "
               + " AND UPPER(" + app.config['DB_USERS_EMAIL'] +
               ") != UPPER('" + usrEmail + "') "
               + group
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

            if isFriend:
                cursor.execute("SELECT " + app.config['DB_RECORD_DISTANCE'] + " FROM " +
                               app.config['DB_TABLE_RECORDS'] + " WHERE users_id = " + str(res[0]) + ";")

                resultDist = cursor.fetchall()

                totDist = 0
                for record in resultDist:
                    totDist += record[0]

                jres['totalDistance'] = totDist

                try:
                    jres['email'] = res[5]
                    jres['isLive'] = res[6]

                    pass
                except Exception as identifier:
                    jres['isLive'] = 0

                    pass

            jsonArr.append(jres)

        pass
    except Exception as identifier:

        pass

    cursor.close()
    conn.close()

    return jsonArr


# gets all friend requests the user got from other users
def getFriendRequests(userId):
    conn = mysql.connect()
    cursor = conn.cursor()

    janswerArr = []

    try:
        sql = ("SELECT " + app.config['DB_USERS_HAS_USERS_ASKER']
               + " FROM " + app.config['DB_TABLE_HAS_USERS']
               + " WHERE "
               + app.config['DB_USERS_HAS_USERS_ASKED']
               + " = %s AND "
               + app.config['DB_USERS_HAS_USERS_AF'] + " = 0;")

        cursor.execute(sql, (userId,))

        result = cursor.fetchall()

        for res in result:
            janswerArr.append(getFriendById(res[0]))
    except Exception as identifier:
        pass

    cursor.close()
    conn.close()

    return janswerArr


# gets all friend requests the user has sent
def showMyFriendRequests(userId):
    conn = mysql.connect()
    cursor = conn.cursor()

    janswerArr = []

    try:
        sql = ("SELECT " + app.config['DB_USERS_HAS_USERS_ASKED']
               + " FROM " + app.config['DB_TABLE_HAS_USERS']
               + " WHERE "
               + app.config['DB_USERS_HAS_USERS_ASKER']
               + " = %s AND "
               + app.config['DB_USERS_HAS_USERS_AF'] + " = 0;")

        cursor.execute(sql, (userId,))

        result = cursor.fetchall()

        for res in result:
            janswerArr.append(getFriendById(res[0]))
    except Exception as identifier:
        pass

    cursor.close()
    conn.close()

    return janswerArr


# request friendship, if already arequest exists create friendship
def requestFriend(friendId, userId):
    conn = mysql.connect()
    cursor = conn.cursor()

    success = 1

    try:
        sql = ("SELECT * FROM " + app.config['DB_TABLE_HAS_USERS']
               + " WHERE "
               + app.config['DB_USERS_HAS_USERS_ASKER'] + " = %s AND "
               + app.config['DB_USERS_HAS_USERS_ASKED'] + " = %s AND "
               + app.config['DB_USERS_HAS_USERS_AF'] + " = 0;")

        cursor.execute(sql, (friendId, userId,))

        result = cursor.fetchone()

        if result != None:
            sql = ("UPDATE " + app.config['DB_TABLE_HAS_USERS']
                   + " SET " + app.config['DB_USERS_HAS_USERS_AF'] + " = 1, "
                   + app.config['DB_USERS_HAS_USERS_DOF']
                   + " = %s WHERE "
                   + app.config['DB_USERS_HAS_USERS_ASKER'] + " = %s AND "
                   + app.config['DB_USERS_HAS_USERS_ASKED'] + " = %s AND "
                   + app.config['DB_USERS_HAS_USERS_AF'] + " = 0;"
                   )
            success = 2
            cursor.execute(sql, (int(time.time()), friendId, userId,))

        else:
            sql = ("INSERT INTO " + app.config['DB_TABLE_HAS_USERS'] + " ("
                   + app.config['DB_USERS_HAS_USERS_ASKER'] + ", "
                   + app.config['DB_USERS_HAS_USERS_ASKED'] + ") VALUES (%s, %s);")

            success = 0
            cursor.execute(sql, (userId, friendId,))

        conn.commit()

        pass
    except Exception as identifier:
        success = 1

        pass
    cursor.close()
    conn.close()

    return success


def getLiveRecord(friendId, userId, index):
    janswer = {}

    conn = mysql.connect()
    cursor = conn.cursor()

    try:

        userJson = showFriendProfile(friendId, userId)

        if userJson['firstName'] != None:
            sql = ("SELECT " + app.config['DB_LIVE_RECORD_ID'] + ", "
                   + app.config['DB_LIVE_RECORD_TIME'] + ", "
                   + app.config['DB_LIVE_RECORD_TYPE'] + ", "
                   + app.config['DB_LIVE_RECORD_RIDETIME'] + ", "
                   + app.config['DB_LIVE_RECORD_DISTANCE']
                   + " FROM " + app.config['DB_TABLE_LIVE_RECORDS']
                   + " WHERE " + app.config['DB_LIVE_RECORD_USERS_ID_FK']
                   + " = %s;")

            cursor.execute(sql, (friendId,))

            result = cursor.fetchone()

            janswer['firstName'] = userJson['firstName']
            janswer['lastName'] = userJson['lastName']
            janswer['profileId'] = int(friendId)
            janswer['id'] = result[0]
            janswer['time'] = result[1]
            janswer['type'] = result[2]
            janswer['rideTime'] = result[3]
            janswer['distance'] = result[4]
            janswer['locations'] = []

            sql = ("SELECT " + app.config['DB_LOCATION_LATITUDE'] + ", "
                   + app.config['DB_LOCATION_LONGITUDE'] + ", "
                   + app.config['DB_LOCATION_ALTITUDE'] + ", "
                   + app.config['DB_LOCATION_TIME'] + ", "
                   + app.config['DB_LOCATION_SPEED'] + ", "
                   + app.config['DB_LOCATION_ID']
                   + " FROM " + app.config['DB_TABLE_LOCATIONS']
                   + " WHERE "
                   + app.config['DB_LOCATION_ID'] + " > %s AND "
                   + app.config['DB_LOCATION_RECORD_ID'] + " = %s;")

            cursor.execute(sql, (index, result[0],))

            locations = cursor.fetchall()

            for location in locations:
                jloc = {}
                jloc['latitude'] = location[0]
                jloc['longitude'] = location[1]
                jloc['altitude'] = location[2]
                jloc['time'] = location[3]
                jloc['speed'] = location[4]
                jloc['id'] = location[5]

                janswer['locations'].append(jloc)

        pass
    except Exception as identifier:
        pass

    cursor.close()
    conn.close()

    return janswer


def getLiveFriends(userId):
    jsonArr = []

    try:
        conn = mysql.connect()
        cursor = conn.cursor()

        sql = ("SELECT " + app.config['DB_TABLE_USERS'] + "." + app.config['DB_USERS_ID'] + ", "
               + app.config['DB_TABLE_USERS'] + "." +
               app.config['DB_USERS_FIRSTNAME'] + ", "
               + app.config['DB_TABLE_USERS'] + "." +
               app.config['DB_USERS_LASTNAME'] + ", "
               + app.config['DB_TABLE_USERS'] +
               "." + app.config['DB_USERS_IMAGE'] + ", "
               + app.config['DB_TABLE_USERS'] + "." +
               app.config['DB_USERS_DATEOFREGISTRATION'] + ", "
               + app.config['DB_TABLE_USERS'] +
               "." + app.config['DB_USERS_EMAIL']
               + " FROM " + app.config['DB_TABLE_USERS'] + " INNER JOIN "
               + app.config['DB_TABLE_HAS_USERS'] + " ON "
               + app.config['DB_TABLE_USERS'] + "." +
               app.config['DB_USERS_ID'] + " = "
               + app.config['DB_TABLE_HAS_USERS'] + "." +
               app.config['DB_USERS_HAS_USERS_ASKER'] + " OR "
               + app.config['DB_TABLE_USERS'] + "." +
               app.config['DB_USERS_ID'] + " = "
               + app.config['DB_TABLE_HAS_USERS'] + "." +
               app.config['DB_USERS_HAS_USERS_ASKED']
               + " INNER JOIN " + app.config['DB_TABLE_LIVE_RECORDS'] + " ON "
               + app.config['DB_TABLE_USERS'] + "." +
               app.config['DB_USERS_ID'] + " = "
               + app.config['DB_TABLE_LIVE_RECORDS'] + "." +
               app.config['DB_LIVE_RECORD_USERS_ID_FK'] + " OR "
               + app.config['DB_TABLE_USERS'] + "." +
               app.config['DB_USERS_ID'] + " = "
               + app.config['DB_TABLE_LIVE_RECORDS'] + "." +
               app.config['DB_LIVE_RECORD_USERS_ID_FK']
               + " WHERE " + app.config['DB_TABLE_USERS'] +
               "." + app.config['DB_USERS_ID']
               + " != %s AND " +
               app.config['DB_TABLE_HAS_USERS'] + "." +
               app.config['DB_USERS_HAS_USERS_AF']
               + " = 1 AND (" + app.config['DB_TABLE_HAS_USERS'] +
               "." + app.config['DB_USERS_HAS_USERS_ASKED']
               + " = %s OR "
               + app.config['DB_TABLE_HAS_USERS'] + "." +
               app.config['DB_USERS_HAS_USERS_ASKER'] + " = %s);"
               )
        cursor.execute(sql, (userId, userId, userId,))

        result = cursor.fetchall()

        for res in result:
            jres = {}
            jres['id'] = res[0]
            jres['firstName'] = res[1]
            jres['lastName'] = res[2]
            jres['image'] = res[3]
            jres['dateOfRegistration'] = res[4]
            jres['email'] = res[5]

            jres['distance'] = getUserTotalDistance(res[0])

            jsonArr.append(jres)

        pass
    except Exception as identifier:
        pass
    finally:
        cursor.close()
        conn.close()
        pass

    return jsonArr


def deleteLiveRecord(userId):
    success = 1
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        sql = ("DELETE FROM " + app.config['DB_TABLE_LIVE_RECORDS']
               + " WHERE " + app.config['DB_LIVE_RECORD_USERS_ID_FK']
               + " = %s;")

        cursor.execute(sql, (userId,))
        conn.commit()
        success = 0
        pass
    except Exception as identifier:
        success = 1
        pass
    finally:
        cursor.close()
        conn.close()
        pass
    return success


# request reset password
def resetUserPassword(email):
    conn = mysql.connect()
    cursor = conn.cursor()

    baseUrl = app.config['BASE_URL']+"/resetPassword?email="+email+"&token="
    try:
        sql = ('SELECT ' + app.config['DB_USERS_FIRSTNAME']
               + ', ' + app.config['DB_USERS_ID'] + ' FROM ' +
               app.config['DB_TABLE_USERS'] + ' WHERE '
               + app.config['DB_USERS_EMAIL'] + ' = %s;')

        cursor.execute(sql, (email,))

        result = cursor.fetchone()

        firstname = result[0]
        userId = result[1]

        token = generateVerifyToken(
            firstname, "", email)

        sql = ('UPDATE ' + app.config['DB_TABLE_USERS']
               + ' SET ' + app.config['DB_USERS_RESETTOKEN']
               + ' = %s ' + ' WHERE ' + app.config['DB_USERS_ID']
               + ' = %s;')
        cursor.execute(sql, (token, userId,))
        conn.commit()

        deleteLink = app.config['BASE_URL'] + \
            "/deleteResetRequest?email="+email+"&token=" + token

        # Start mail sending thread
        thread = Thread(target=sendResetMail, args=(
            email, firstname, baseUrl + token, deleteLink, ))
        thread.start()
        return 1
        pass
    except Exception as identifier:
        return 0
        pass
    finally:
        cursor.close()
        conn.close()
        pass

    return baseUrl


###########################
###    WEB API-Pages    ###
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

# Reset password
@app.route("/reset", methods=['GET'])
def resetPage():
    if current_user.is_authenticated:
        return redirect("/dashboard")
    else:
        alertType = request.args.get('alert')
        return render_template("resetPassword.html", alert=alertType)

# Profile page
@app.route("/dashboard", methods=["GET"])
def dashboardPage():
    if current_user.is_authenticated:
        totalRecords = getRecordsAmount(current_user.id)
        totalDistance = getUserTotalDistance(current_user.id)
        totalTime = getTotalRecordTime(current_user.id)
        totalPauseTime = getTotalPauseTime(current_user.id)
        return render_template("dashboard.html", user=current_user, site="dashboard", recordsAmount=totalRecords, totalDistance=totalDistance, totalTime=totalTime, totalPauseTime=totalPauseTime)
    else:
        return redirect("/login")

# Profile page
@app.route("/profile", methods=["GET"])
def profilePage():
    if current_user.is_authenticated:
        userId = request.args.get('id')
        backOpt = request.args.get('back')

        if userId:
            try:
                profileData = showFriendProfile(userId, current_user.id)
                totalRecords = getRecordsAmount(userId)
                totalDistance = getUserTotalDistance(userId)
                totalTime = getTotalRecordTime(userId)
                pass
            except Exception as identifier:
                userData = None
                pass
            return render_template("profile.html", site="other_profile", user=current_user, profileData=profileData, recordsAmount=totalRecords, totalDistance=totalDistance, totalTime=totalTime, back=backOpt)
        else:
            totalRecords = getRecordsAmount(current_user.id)
            totalDistance = getUserTotalDistance(current_user.id)
            totalTime = getTotalRecordTime(current_user.id)
            return render_template("profile.html", site="profile", user=current_user, profileData=current_user, recordsAmount=totalRecords, totalDistance=totalDistance, totalTime=totalTime, back=backOpt)
    else:
        return redirect("/login")

# Profile page
@app.route("/settings", methods=["GET"])
def settingsPage():
    if current_user.is_authenticated:
        alertType = request.args.get('alert')
        return render_template("settings.html", site="settings", user=current_user, alert=alertType)
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
        page = request.args.get('page')
        if page == None:
            page = 1
        amount = math.ceil(getRecordsAmount(current_user.id)/10)
        records = getRecordsByID(current_user.id, int(page))
        alertType = request.args.get('alert')
        return render_template("records.html", user=current_user, site="records", records=records, amount=amount, alert=alertType)
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
        return render_template("single-record.html", site="record", user=current_user, recordData=recordData, alert=alertType)
    else:
        return redirect("/login")

# Search persons page
@app.route("/community/search", methods=["GET"])
def searchPage():
    if current_user.is_authenticated:
        searchQuery = request.args.get('search')
        if searchQuery != None:
            searchresults = searchFriends(
                0, searchQuery, None, current_user.email)
        else:
            searchresults = None
        alertType = request.args.get('alert')
        return render_template("search.html", user=current_user, site="search", searchresults=searchresults, alert=alertType)
    else:
        return redirect("/login")

# Show friend list
@app.route("/community/friends", methods=["GET"])
def friendsPage():
    if current_user.is_authenticated:
        page = request.args.get('page')
        if page == None:
            page = 1
        amount = getFriendsAmount(current_user.id)
        friends = searchFriends(
            int(page), "", current_user.id, current_user.email)
        alertType = request.args.get('alert')
        return render_template("friends.html", user=current_user, site="friends", friends=friends, amount=amount, alert=alertType)
    else:
        return redirect("/login")

# Show friend requests
@app.route("/community/friendrequests", methods=["GET"])
def friendRequestsPage():
    if current_user.is_authenticated:
        requestType = request.args.get('type')
        incommings = getFriendRequests(current_user.id)
        outgoings = showMyFriendRequests(current_user.id)
        alertType = request.args.get('alert')
        return render_template("friendrequests.html", user=current_user, site="friendrequests", type=requestType, incommings=incommings, outgoings=outgoings, alert=alertType)
    else:
        return redirect("/login")

# Show live friends
@app.route("/community/live", methods=["GET"])
def livePage():
    if current_user.is_authenticated:
        alertType = request.args.get('alert')
        profileId = request.args.get('id')
        if profileId:
            livefriend = getLiveRecord(profileId, current_user.id, 0)
            return render_template("live.html", user=current_user, site="live", livefriend=livefriend, alert=alertType)
        else:
            livefriends = getLiveFriends(current_user.id)
            return render_template("livelist.html", user=current_user, site="live", livefriends=livefriends, alert=alertType)
    else:
        return redirect("/login")

#####################################
###   WEB API-Handler Functions   ###
#####################################

# Handle login
@app.route("/login", methods=['POST'])
def login():
    # get user from db instantiate user

    if validateLogin(request.form['email'], hash256Password(request.form['password'])):
        user = user_loader(request.form['email'])

        # Set lifetime session
        if request.form.get('lifetime') == 'on':
            app.config['SESSION_LIFETIME'] = True
        else:
            app.config['SESSION_LIFETIME'] = False

        conn = mysql.connect()
        cursor = conn.cursor()

        sql = ('SELECT ' + app.config['DB_USERS_VERIFYTOKEN']
               + ' FROM '+app.config['DB_TABLE_USERS']
               + ' WHERE ' + app.config['DB_USERS_ID']
               + ' = %s;')

        cursor.execute(sql, (user.id,))

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

# Reset password
@app.route("/resetPassword", methods=['POST'])
def resetPassword():
    if resetUserPassword(request.form['email']):
        flash('Die Email zum Zürücksetzen des Passworts wurde an "' +
              request.form['email'] + '" gesendet. Bitte überprüfen Sie Ihr Email-Postfach.')
        return redirect("/reset?alert=success")
    else:
        flash('Die Email-Adresse "' +
              request.form['email'] + '" konnte keinem Konto zugeordnet werden!')
        return redirect("/reset?alert=danger")

# Register a user
@app.route("/registerUser", methods=['POST'])
def registerUser():
    # Add validation
    success = registerUserDB(
        request.form['firstName'],
        request.form['lastName'],
        request.form['email'],
        request.form['password1'],
        int(calendar.timegm(datetime.strptime(
            request.form['birthday'], '%Y-%m-%d').utctimetuple())),
        request.form['genderRadio'])

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
        birthday = int(calendar.timegm(datetime.strptime(
            request.form['birthday'], '%Y-%m-%d').utctimetuple()))
        success = updateUserDB(current_user.id, birthday,
                               request.form['firstName'], request.form['lastName'],
                               request.form['genderRadio'], request.form['size'],
                               request.form['weight'], None, str(int(time.time())), None, None)

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
                               None, None, None, None, image, None, None, None)

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
                current_user.id, hash256Password(request.form['currentPass']),
                hash256Password(request.form['newPass']), str(int(time.time())))

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

# Add friend to friendlist
@app.route("/addFriend", methods=['POST'])
def addFriend():
    if current_user.is_authenticated:
        success = requestFriend(request.form['profileId'], current_user.id)

        if success == 2:
            flash('Sie sind jetzt mit "' +
                  request.form['profileName'] + '" befreundet.')
            return redirect("/community/friends?alert=success")
        if success == 0:
            flash('Eine Freundschaftsanfrage an "' +
                  request.form['profileName'] + '" wurde versendet.')
            return redirect("/community/friends?alert=success")
        else:
            flash('Unbekannter Fehler beim Senden der Freundschaftsanfrage!')
            return redirect("/community/friends?alert=danger")
    else:
        return redirect("/login")

# Remove friend from friendlist
@app.route("/removeFriend", methods=['POST'])
def removeFriend():
    if current_user.is_authenticated:
        success = deleteFriend(request.form['profileId'], current_user.id)

        if success == 0:
            flash('Freund/in "' +
                  request.form['profileName'] + '" wurde erfolgreich entfernt.')
            return redirect("/community/friends?alert=success")
        else:
            flash('Unbekannter Fehler beim Entfernen des/der Freundes/Freundin!')
            return redirect("/community/friends?alert=danger")
    else:
        return redirect("/login")


@app.route("/getLiveRecord", methods=['POST'])
def getLiveRecordWeb():
    friendId = request.form['friendId']
    index = request.form['index']

    janswer = getLiveRecord(friendId, current_user.id, index)
    return json.dumps(janswer)

# Search for profile
@app.route("/search", methods=['POST'])
def search():
    if current_user.is_authenticated:
        searchParam = request.form['searchParam']
        return redirect("/community/search?search=" + searchParam)
    else:
        return redirect("/login")

# Get image from user
@app.route("/image", methods=['GET'])
def getImage():
    try:
        userID = request.args.get('userID')

        conn = mysql.connect()
        cursor = conn.cursor()

        sql = ('SELECT '+app.config['DB_USERS_IMAGE']+' FROM '
               + app.config['DB_TABLE_USERS'] + ' WHERE '
               + app.config['DB_USERS_ID']+' = %s;')

        cursor.execute(sql, (userID,))

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

    conn = mysql.connect()
    cursor = conn.cursor()
    try:

        sql = ('UPDATE '+app.config['DB_TABLE_USERS'] + ' SET '
               + app.config['DB_USERS_VERIFYTOKEN']+' = NULL WHERE '
               + app.config['DB_USERS_EMAIL']+' = %s AND '
               + app.config['DB_USERS_VERIFYTOKEN']+' = %s;')

        cursor.execute(sql, (email, token,))

        conn.commit()
        cursor.close()
        conn.close()
        return render_template("verification.html", state=1)
        pass
    except Exception as identifier:
        cursor.close()
        conn.close()
        return render_template("verification.html", state=0)
        pass


# reset Password
@app.route("/resetPassword", methods=['GET'])
def resetPasswordFunction():
    email = request.args.get('email')
    token = request.args.get('token')

    conn = mysql.connect()
    cursor = conn.cursor()

    try:
        sql = ('SELECT ' + app.config['DB_USERS_ID']
               + ' FROM '
               + app.config['DB_TABLE_USERS']
               + ' WHERE '+app.config['DB_USERS_EMAIL']+' = %s AND '
               + app.config['DB_USERS_RESETTOKEN']+' = %s;')

        cursor.execute(sql, (email, token,))

        result = cursor.fetchone()

        cursor.close()
        conn.close()

        if result != None:
            return render_template("newPassword.html", token=token, email=email)
        else:
            return redirect("/")

        pass
    except Exception as identifier:

        cursor.close()
        conn.close()
        return redirect("/")
        pass


# reset set new Password
@app.route("/newPassword", methods=['POST'])
def newPassword():
    token = request.form['resetToken']
    newPasswordOne = request.form['password1']
    newPasswordTwo = request.form['password2']
    email = request.form['email']

    if newPasswordOne == newPasswordTwo:
        conn = mysql.connect()
        cursor = conn.cursor()

        success = ""

        try:
            sql = ('UPDATE ' + app.config['DB_TABLE_USERS']
                   + ' SET ' + app.config['DB_USERS_RESETTOKEN'] + ' = NULL, '
                   + app.config['DB_USERS_PASSWORD'] + ' = %s WHERE '
                   + app.config['DB_USERS_EMAIL'] + ' = %s AND '
                   + app.config['DB_USERS_RESETTOKEN'] + ' = %s;')

            password = hash256Password(newPasswordOne)

            cursor.execute(sql, (pbkdf2_sha256.hash(password), email, token,))

            conn.commit()
            flash('Das Passwort wurde erfolgreich geändert!')
            success = "?alert=success"
            pass
        except Exception as identifier:
            flash('Das Passwort konnte nicht gändert werden. Versuchen Sie es erneut.')
            success = "?alert=danger"

            pass
        finally:
            cursor.close()
            conn.close()
            pass
        return redirect("/" + success)

    else:
        flash('Die Eingaben müssen identisch sein!')
        return render_template("newPassword.html", token=token, email=email)


@app.route("/deleteResetRequest", methods=['GET'])
def deleteResetRequest():
    token = request.args.get('token')
    email = request.args.get('email')

    conn = mysql.connect()
    cursor = conn.cursor()

    try:
        sql = ('UPDATE ' + app.config['DB_TABLE_USERS']
               + ' SET ' + app.config['DB_USERS_RESETTOKEN'] + ' = NULL WHERE '
               + app.config['DB_USERS_EMAIL'] + ' = %s AND '
               + app.config['DB_USERS_RESETTOKEN'] + ' = %s;')

        cursor.execute(sql, (email, token,))

        conn.commit()
        flash('Passwort-reset erfolgreich abgebrochen!')
        pass
    except Exception as identifier:
        flash('Passwort-reset konnte nicht abgebrochen werden!')
        pass
    finally:
        cursor.close()
        conn.close()
        pass
    return redirect("/")


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

    sql = ('SELECT ' + app.config['DB_USERS_ID'] + ', '
           + app.config['DB_USERS_VERIFYTOKEN'] + ' FROM '
           + app.config['DB_TABLE_USERS'] + ' WHERE '
           + app.config['DB_USERS_EMAIL']+' = %s;')

    cursor.execute(sql, (request.authorization.username,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    jsonObj = {}
    jsonObj['userData'] = getUserWithImageFromDB(result[0])
    jsonObj['records'] = getRecordsByID(result[0], 0)

    if result[1] == None:
        jsonObj['success'] = 0
    else:
        jsonObj['success'] = 2

    response = make_response(json.dumps(jsonObj))
    response.mimetype = "application/json"

    return response

# Create new user in database
@app.route("/registerAPI", methods=['POST'])
def registerAPI():
    jsonRequest = request.json

    jsonObj = {}
    jsonObj['success'] = registerUserDB(
        jsonRequest['firstName'], jsonRequest['lastName'], jsonRequest['email'],
        jsonRequest['password'],  jsonRequest['dateOfBirth'],  jsonRequest['gender'])

    response = make_response(json.dumps(jsonObj))
    response.mimetype = "application/json"

    return response

# Get all userdata with image by id
@app.route("/getUserByIdAPI", methods=['POST'])
@requires_authorization
def getUserByIdAPI():
    response = make_response(json.dumps(
        getUserWithImageFromDB(request.json['id'])))
    response.mimetype = "application/json"
    return response

# Get all Records by userId and Page
@app.route("/getRecordsByIdAPI", methods=['POST'])
@requires_authorization
def getRecordsByIdAPI():
    response = make_response(json.dumps(getRecordsByID(
        request.json['id'], int(request.json['page']))))
    response.mimetype = "application/json"
    return response

# Edit record name
@app.route("/editRecordAPI", methods=['POST'])
def editRecordAPI():
    j = request.json

    jsonSuccess = {}
    if updateRecordDB(j['recordId'], j['recordName'], j['timestamp']):
        jsonSuccess['success'] = 0
    else:
        jsonSuccess['success'] = 1

    response = make_response(json.dumps(jsonSuccess))
    response.mimetype = "application/json"

    return response

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

    try:
        timestamp = j['timeStamp']
        pass
    except Exception as identifier:
        timestamp = None
        pass

    userId = getUserId(email)

    if updateUserDB(userId, dateOfBirth, firstName, lastName, gender, size, weight, image, timestamp, hints, darkTheme):
        jsonSuccess['success'] = 0
    else:
        jsonSuccess['success'] = 1

    response = make_response(json.dumps(jsonSuccess))
    response.mimetype = "application/json"

    return response

# Change user password
@app.route("/changeUserPasswordAPI", methods=['POST'])
@requires_authorization
def changeUserPasswordAPI():
    jsonSuccess = {}

    usrId = getUserId(request.authorization.username)

    jsonSuccess['success'] = changeUserPasswordDB(usrId, request.authorization.password,
                                                  request.json['newPw'], request.json['timeStamp'])

    response = make_response(json.dumps(jsonSuccess))
    response.mimetype = "application/json"

    return response


# Synchronize user data with app database
@app.route("/synchronizeDataAPI", methods=['POST'])
@requires_authorization
def synchronizeDataAPI():
    conn = mysql.connect()
    cursor = conn.cursor()

    auth = request.authorization
    usrid = getUserId(auth.username)

    params = "timeStamp"

    sql = ('SELECT ' + params + ' FROM '
           + app.config['DB_TABLE_USERS'] + ' WHERE '
           + app.config['DB_USERS_ID']+' = %s;')

    cursor.execute(sql, (usrid,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    jsonAnswer = {}

    if(int(request.json['timeStamp']) < result[0]):
        jsonAnswer['state'] = 0
        jsonAnswer['user'] = getUserWithImageFromDB(usrid)
    elif (int(request.json['timeStamp']) == result[0]):
        jsonAnswer['state'] = 2
        jsonAnswer['user'] = None
    else:
        jsonAnswer['state'] = 1
        jsonAnswer['user'] = None

    response = make_response(json.dumps(jsonAnswer))
    response.mimetype = "application/json"

    return response


@app.route("/deleteUserAPI", methods=['POST'])
@requires_authorization
def deleteUserAPI():
    jsonSuccess = {}
    jsonSuccess['success'] = deleteUserById(request.json['id'])

    response = make_response(json.dumps(jsonSuccess))
    response.mimetype = "application/json"

    return response


@app.route("/uploadTrackAPI", methods=['POST'])
@requires_authorization
def uploadTrackAPI():
    jsonSuccess = {}

    auth = request.authorization
    userid = getUserId(auth.username)

    conn = mysql.connect()
    cursor = conn.cursor()

    try:
        jsonTrack = request.json

        sql = ('INSERT INTO ' + app.config['DB_TABLE_RECORDS'] + ' ('
               + app.config['DB_RECORD_NAME'] + ','
               + app.config['DB_RECORD_TIME'] + ','
               + app.config['DB_RECORD_DATE'] + ','
               + app.config['DB_RECORD_TYPE'] + ','
               + app.config['DB_RECORD_RIDETIME'] + ','
               + app.config['DB_RECORD_DISTANCE'] + ','
               + app.config['DB_RECORD_TIMESTAMP'] + ','
               + app.config['DB_RECORD_USERS_ID'] + ','
               + app.config['DB_RECORD_LOCATION_DATA'] + ') VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);')

        for loc in jsonTrack['locations']:
            del loc[app.config['ANDROID_LOCATION_RECORD_ID']]

        cursor.execute(sql, (jsonTrack['name'],
                             jsonTrack['time'],
                             jsonTrack['date'],
                             jsonTrack['type'],
                             jsonTrack['rideTime'],
                             jsonTrack['distance'],
                             jsonTrack['timeStamp'],
                             jsonTrack['userId'],
                             json.dumps(jsonTrack['locations']),))

        conn.commit()

        jsonSuccess['success'] = 0
        jsonSuccess['record'] = getSingleRecordByID(cursor.lastrowid)
        jsonSuccess['oldId'] = jsonTrack['id']

        deleteLiveRecord(userid)

        pass
    except Exception as identifier:
        jsonSuccess['success'] = 1
        pass
    cursor.close()
    conn.close()

    response = make_response(json.dumps(jsonSuccess))
    response.mimetype = "application/json"

    return response


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

    auth = request.authorization
    usrid = getUserId(auth.username)

    for jsn in jarr:
        ids.append(int(jsn['id']))

        sql = ('SELECT ' + app.config['DB_RECORD_TIMESTAMP'] + ", "
               + app.config['DB_RECORD_NAME'] + ' FROM '
               + app.config['DB_TABLE_RECORDS'] + ' WHERE '
               + app.config['DB_RECORD_ID']+' = %s;')

        cursor.execute(sql, (jsn['id'],))
        result = cursor.fetchone()

        timeStamp = int(jsn['timeStamp'])

        if result == None:
            # record not in Server DB
            janswer['missingId'].append(jsn['id'])
        elif result[0] < timeStamp:
            # update Recordname
            updateRecordDB(jsn['id'], jsn['name'], jsn['timeStamp'])
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

            sql = ("SELECT " + app.config['DB_RECORD_ID'] + " FROM " + app.config['DB_TABLE_RECORDS'] +
                   " WHERE " + app.config['DB_RECORD_USERS_ID']
                   + " = " + str(usrid) + " AND " + app.config['DB_RECORD_ID'] +
                   " NOT IN ({});".format(placeholders))

            cursor.execute(sql, tuple(ids))

            result = cursor.fetchall()

        else:
            sql = ("SELECT " + app.config['DB_RECORD_ID']
                   + " FROM " + app.config['DB_TABLE_RECORDS']
                   + " WHERE " + app.config['DB_RECORD_USERS_ID']
                   + " = %s;")

            cursor.execute(sql, (usrid,))

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

        sql = ("SELECT " + app.config['DB_RECORD_ID'] + " FROM "
               + app.config['DB_TABLE_RECORDS'] + " WHERE "
               + app.config['DB_RECORD_USERS_ID'] + " = %s;")

        cursor.execute(sql, (usrid,))

        idsInDB = []

        result = cursor.fetchall()

        for res in result:
            idsInDB.append(res[0])

        deletedIds = list(set(ids) - set(idsInDB))

        for delID in deletedIds:
            jid = {}
            jid['id'] = delID
            janswer['deletedOnServer'].append(jid)

        pass
    except Exception as identifier:
        print(identifier)
        pass

    cursor.close()
    conn.close()

    response = make_response(json.dumps(janswer))
    response.mimetype = "application/json"

    return response


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

        sql = ('DELETE FROM ' + app.config['DB_TABLE_RECORDS'] + " WHERE "
               + app.config['DB_RECORD_ID']
               + " = " + jrequest['recordId'] + " AND "
               + app.config['DB_RECORD_USERS_ID'] + " = %s;")

        cursor.execute(sql, (usrid,))
        conn.commit()
        jsonAnswer['success'] = 0
        pass
    except Exception as identifier:
        jsonAnswer['success'] = 1
        pass

    cursor.close()
    conn.close()

    response = make_response(json.dumps(jsonAnswer))
    response.mimetype = "application/json"

    return response


@app.route("/searchFriendsAPI", methods=['POST'])
@requires_authorization
def searchFriendsAPI():
    jrequest = request.json

    auth = request.authorization

    page = int(jrequest['page'])
    search = jrequest['search']

    jsonArr = searchFriends(page, search, None, auth.username)

    response = make_response(json.dumps(jsonArr))
    response.mimetype = "application/json"

    return response


@app.route("/searchMyFriendsAPI", methods=['POST'])
@requires_authorization
def searchMyFriendsAPI():
    jrequest = request.json

    auth = request.authorization
    usrid = getUserId(auth.username)

    page = int(jrequest['page'])
    search = jrequest['search']

    jsonArr = searchFriends(page, search, usrid, auth.username)

    response = make_response(json.dumps(jsonArr))
    response.mimetype = "application/json"

    return response


@app.route("/requestFriendAPI", methods=['POST'])
@requires_authorization
def requestFriendAPI():
    jrequest = request.json

    friendId = int(jrequest['friendId'])

    auth = request.authorization
    usrid = getUserId(auth.username)

    janswer = {}

    janswer['success'] = requestFriend(friendId, usrid)

    response = make_response(json.dumps(janswer))
    response.mimetype = "application/json"

    return response


@app.route("/showFriendRequestsAPI", methods=['POST'])
@requires_authorization
def showFriendRequestsAPI():
    auth = request.authorization
    usrid = getUserId(auth.username)

    response = make_response(json.dumps(getFriendRequests(usrid)))
    response.mimetype = "application/json"

    return response


@app.route("/showMyFriendRequestsAPI", methods=['POST'])
@requires_authorization
def showMyFriendRequestsAPI():
    auth = request.authorization
    usrid = getUserId(auth.username)

    response = make_response(json.dumps(showMyFriendRequests(usrid)))
    response.mimetype = "application/json"

    return response


@app.route("/showStrangerProfileAPI", methods=['POST'])
@requires_authorization
def showStrangerProfileAPI():
    jrequest = request.json

    strangerId = int(jrequest['strangerId'])

    auth = request.authorization
    usrid = getUserId(auth.username)

    jres = showFriendProfile(strangerId, usrid)

    response = make_response(json.dumps(jres))
    response.mimetype = "application/json"

    return response


@app.route("/showFriendProfileAPI", methods=['POST'])
@requires_authorization
def showFriendProfileAPI():
    jrequest = request.json

    auth = request.authorization
    usrid = getUserId(auth.username)

    friendId = int(jrequest['friendId'])

    friend = showFriendProfile(friendId, usrid)

    response = make_response(json.dumps(friend))
    response.mimetype = "application/json"

    return response


@app.route("/deleteFriendAPI", methods=['POST'])
@requires_authorization
def deleteFriendAPI():
    jrequest = request.json

    auth = request.authorization
    usrid = getUserId(auth.username)

    friendId = int(jrequest['friendId'])

    janswer = {}
    janswer['success'] = deleteFriend(friendId, usrid)

    response = make_response(json.dumps(janswer))
    response.mimetype = "application/json"

    return response


@app.route("/requestLiveRecordAPI", methods=['POST'])
@requires_authorization
def requestLiveRecordAPI():
    auth = request.authorization
    usrid = getUserId(auth.username)

    janswer = {}

    conn = mysql.connect()
    cursor = conn.cursor()

    try:
        sql = ("DELETE FROM " + app.config['DB_TABLE_LIVE_RECORDS']
               + " WHERE " + app.config['DB_LIVE_RECORD_USERS_ID_FK']
               + " = %s;")

        cursor.execute(sql, (usrid,))

        conn.commit()

        sql = ("INSERT INTO " + app.config['DB_TABLE_LIVE_RECORDS']
               + "(" + app.config['DB_LIVE_RECORD_USERS_ID_FK']
               + ") VALUES (%s);")

        cursor.execute(sql, (usrid,))
        conn.commit()

        janswer['liveRecordId'] = cursor.lastrowid

        pass
    except Exception as identifier:
        pass

    cursor.close()
    conn.close()

    response = make_response(json.dumps(janswer))
    response.mimetype = "application/json"

    return response


@app.route("/updateLiveRecordAPI", methods=['POST'])
@requires_authorization
def updateLiveRecordAPI():
    jrequest = request.json

    jsonSuccess = {}
    jsonSuccess['success'] = 1

    conn = mysql.connect()
    cursor = conn.cursor()

    lrId = jrequest['id']
    time = jrequest['time']
    typeLr = jrequest['type']
    rideTime = jrequest['rideTime']
    distance = jrequest['distance']
    locations = jrequest['locations']

    try:

        sql = ("UPDATE " + app.config['DB_TABLE_LIVE_RECORDS'] + " SET "
               + app.config['DB_LIVE_RECORD_TIME'] + " = %s, "
               + app.config['DB_LIVE_RECORD_TYPE'] + " = %s, "
               + app.config['DB_LIVE_RECORD_RIDETIME'] + " = %s, "
               + app.config['DB_LIVE_RECORD_DISTANCE'] + " = %s WHERE "
               + app.config['DB_LIVE_RECORD_ID'] + " = %s;")

        cursor.execute(sql, (time, typeLr, rideTime, distance, lrId,))
        conn.commit()

        for location in locations:
            sql = ("INSERT INTO " + app.config['DB_TABLE_LOCATIONS'] + " ("
                   + app.config['DB_LOCATION_LATITUDE'] + ", "
                   + app.config['DB_LOCATION_LONGITUDE'] + ", "
                   + app.config['DB_LOCATION_ALTITUDE'] + ", "
                   + app.config['DB_LOCATION_TIME'] + ", "
                   + app.config['DB_LOCATION_SPEED'] + ", "
                   + app.config['DB_LOCATION_RECORD_ID'] + ") VALUES (%s, %s, %s, %s, %s, %s);")

            cursor.execute(sql, (location['latitude'], location['longitude'],
                                 location['altitude'], location['time'],
                                 location['speed'], lrId,))

        conn.commit()
        jsonSuccess['success'] = 0

        pass
    except Exception as identifier:
        jsonSuccess['success'] = 1

        pass

    cursor.close()
    conn.close()

    response = make_response(json.dumps(jsonSuccess))
    response.mimetype = "application/json"

    return response


@app.route("/getLiveRecordAPI", methods=['POST'])
@requires_authorization
def getLiveRecordAPI():
    jrequest = request.json

    friendId = jrequest['friendId']
    index = jrequest['index']

    auth = request.authorization
    userId = getUserId(auth.username)

    janswer = getLiveRecord(friendId, userId, index)

    response = make_response(json.dumps(janswer))
    response.mimetype = "application/json"

    return response


@app.route("/abortLiveRecordAPI", methods=['POST'])
@requires_authorization
def abortLiveRecordAPI():
    auth = request.authorization
    userId = getUserId(auth.username)

    janswer = {}
    janswer['success'] = deleteLiveRecord(userId)

    response = make_response(json.dumps(janswer))
    response.mimetype = "application/json"

    return response


@app.route("/getLiveFriendsAPI", methods=['POST'])
@requires_authorization
def getLiveFriendsAPI():
    auth = request.authorization
    userId = getUserId(auth.username)

    jArr = getLiveFriends(userId)

    response = make_response(json.dumps(jArr))
    response.mimetype = "application/json"

    return response


###########################
###     Flask start     ###
###########################
if __name__ == '__main__':
    app.run(host='0.0.0.0')
