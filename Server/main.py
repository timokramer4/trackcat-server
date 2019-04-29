# vv import Area

from flask import Flask, flash, request, render_template, redirect, jsonify, session
from flaskext.mysql import MySQL
import simplejson
import time
import os
import json

from mailSend import sendVmail

# ^^ import Area

# vv config

app = Flask(__name__)
mysql = MySQL()

app.secret_key = os.urandom(12)
app.config['MYSQL_DATABASE_USER'] = 'remRoot'
app.config['MYSQL_DATABASE_PASSWORD'] = '1Qayse45&'
app.config['MYSQL_DATABASE_DB'] = 'TrackCatDB'
app.config['MYSQL_DATABASE_HOST'] = 'safe-harbour.de'
app.config['MYSQL_DATABASE_PORT'] = 42042
mysql.init_app(app)

# app.config['SECRET_KEY'] = 'hard to guess page'

# ^^ config

# vv testArea

# first test login
# @app.route("/login", methods=['POST'])
# def login():

#     json = request.json

#     print(json)

#     return simplejson.dumps({'success': json['username'] == 'krypto' and json['password'] == 'koffer'})


# ^^ testArea


# vv user Login
def validateLogin(email, password):

    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE email = '" + email + "';")
    result = cursor.fetchone()
    cursor.close()

    return result is not None and password == result[0]  # "a2@Ahhhhh"


def authenticate():
    message = {'message': "Authenticate."}
    resp = jsonify(message)
    resp.status_code = 401
    resp.headers['WWW-Authenticate'] = 'Basic realm="Main"'

    # return resp
    return simplejson.dumps("1")


def requires_authorization(f):
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not validateLogin(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

# ^^ user Login

# Check login and redirect


def checkSession():
    if not session.get('logged_in'):
        return False
    else:
        return True

### Static page routes ###

# Start and login page
@app.route("/", methods=['GET'])
@app.route("/login", methods=['GET'])
def loginPage():
    if not checkSession():
        return render_template("login.html")
    else:
        return redirect("/dashboard")

# LogOut user
@app.route("/logout", methods=['GET'])
def logoutPage():
    session.clear()
    return redirect("/login")

# Register page
@app.route("/register", methods=['GET'])
def registerPage():
    if not session.get('logged_in'):
        return render_template("register.html")
    else:
        return redirect("/dashboard")

# Profile page
@app.route("/dashboard", methods=["GET"])
def dashboardPage():
    if checkSession():
        return render_template("dashboard.html")
    else:
        return redirect("/login")

# Profile page
@app.route("/profile", methods=["GET"])
def profilePage():
    if checkSession():
        return render_template("profile.html")
    else:
        return redirect("/login")

# Profile page
@app.route("/settings", methods=["GET"])
def settingsPage():
    if checkSession():
        return render_template("settings.html")
    else:
        return redirect("/login")

### Web-Handler ###
@app.route("/login", methods=['POST'])
def login():
    if not session.get('logged_in'):
        if validateLogin(request.form['email'], request.form['password']):
            session['logged_in'] = True
            return redirect("/dashboard")
        else:
            flash('Die eingegebenen Zugangsdaten sind falsch!')
            return redirect("/login")
    else:
        return redirect("/dashboard")

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

### BOTH-Handler ###


def registerUserDB(firstName, lastName, email, password):
    # 0 = Valid
    # 1 = Creation error
    # 3 = Email already exists

    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (firstName, lastName, eMail, password, dateOfRegistration, lastLogin, darkTheme,showHelp, timeStamp) VALUES ('" +
                       firstName + "', '" + lastName + "', '" + email + "', '" + password + "', " + str(int(time.time())) + ", " +
                       str(int(time.time())) + ", 0, 1, "+str(int(time.time())) + ");")

        conn.commit()
        cursor.close()

        pass
    except Exception as identifier:
        print(identifier)

        if(identifier.args[0] == 1062):
            if('eMail_UNIQUE' in identifier.args[1]):
                return 3
            return 1

    pass

    sendVmail(email, firstName, "http://safe-harbour.de:4242")

    return 0

### API-Handler ###
@app.route("/loginAPI", methods=['POST'])
@requires_authorization
def loginAPI():
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT idusers,eMail,firstName,lastName,image,gender,weight,size,dateOfBirth,password FROM users WHERE email = '" +
                   request.authorization.username + "';")
    result = cursor.fetchone()
    cursor.close()

    jsonObj = {}
    jsonObj['success'] = 0

    jsonUser = {}

    jsonUser['id'] = result[0]
    jsonUser['eMail'] = result[1]
    jsonUser['firstName'] = result[2]
    jsonUser['lastName'] = result[3]
    jsonUser['image'] = result[4]
    jsonUser['gender'] = result[5]
    jsonUser['weight'] = result[6]
    jsonUser['size'] = result[7]
    jsonUser['dateOfBirth'] = result[8]
    jsonUser['password'] = result[9]

    jsonObj['userData'] = jsonUser

    return json.dumps(jsonObj)


@app.route("/registerAPI", methods=['POST'])
def registerAPI():

    json = request.json

    success = registerUserDB(
        json['firstName'], json['lastName'], json['email'], json['password'])

    return simplejson.dumps(str(success))


if __name__ == '__main__':
    app.run(host='0.0.0.0')
