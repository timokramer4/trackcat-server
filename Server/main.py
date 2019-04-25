# vv import Area

from flask import Flask, request, render_template, redirect, jsonify
from flaskext.mysql import MySQL
import simplejson
import time


# ^^ import Area

# vv config

app = Flask(__name__)
mysql = MySQL()

app.config['MYSQL_DATABASE_USER'] = 'remRoot'
app.config['MYSQL_DATABASE_PASSWORD'] = '1Qayse45&'
app.config['MYSQL_DATABASE_DB'] = 'TrackCatDB'
app.config['MYSQL_DATABASE_HOST'] = 'safe-harbour.de'
app.config['MYSQL_DATABASE_PORT'] = 42042
mysql.init_app(app)

#app.config['SECRET_KEY'] = 'hard to guess string'

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
def check_user_and_password(username, password):

    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT password FROM users WHERE email = '" + username + "';")

    result = cursor.fetchone()
    cursor.close()

    return password == result[0]  # "a2@Ahhhhh"


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
        if not auth or not check_user_and_password(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

# ^^ user Login


### Static page routes ###

# Start and login page
@app.route("/", methods=['GET'])
@app.route("/login", methods=['GET'])
def loginPage():
    return render_template("login.html")

# Register page
@app.route("/register", methods=['GET'])
def registerPage():
    return render_template("register.html")

# Profile page
@app.route("/dashboard", methods=["GET"])
def dashboardPage():
    return render_template("dashboard.html")

# Profile page
@app.route("/profile", methods=["GET"])
def profilePage():
    return render_template("profile.html")

# Profile page
@app.route("/settings", methods=["GET"])
def settingsPage():
    return render_template("settings.html")

### Web-Handler ###


@app.route("/login", methods=['POST'])
def login():
    if check_user_and_password(request.form['email'], request.form['password']):
        return render_template('dashboard.html')
    else:
        return authenticate()

# register a user
@app.route("/registerUser", methods=['POST'])
def registerUser():

    # add validation

    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (firstName, lastName, eMail, password, dateOfRegistration, lastLogin, darkTheme,showHelp, timeStamp) VALUES ('" +
                   request.form['firstName']+"', '"+request.form['lastName']+"', '"+request.form['email']+"', '"+request.form['password1']+"', "+str(int(time.time())) + ", " +
                   str(int(time.time())) + ", 0, 1, "+str(int(time.time())) + ");")

    conn.commit()
    cursor.close()

    return "okay"


### API-Handler ###

@app.route("/loginAPI", methods=['POST'])
@requires_authorization
def loginAPI():
    return simplejson.dumps("0")


@app.route("/registerAPI", methods=['POST'])
def registerAPI():
    json = request.json

    return "okay"


if __name__ == '__main__':
    app.run(host='0.0.0.0')
