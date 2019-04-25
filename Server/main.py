# vv import Area

from flask import Flask, request, render_template, redirect, jsonify
from flaskext.mysql import MySQL
import simplejson


# ^^ import Area

# vv config

app = Flask(__name__)
mysql = MySQL()

app.config['MYSQL_DATABASE_USER'] = 'remRoot'
app.config['MYSQL_DATABASE_PASSWORD'] = '1Qayse45&'
app.config['MYSQL_DATABASE_DB'] = 'TrackCatDB'
app.config['MYSQL_DATABASE_HOST'] = 'safe-harbour.de'
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

    cursor.execute("SELECT * FROM users")

    cursor.close()

    return username == "test@quatsch.de" and password == "a2@Ahhhhh"

def authenticate():
    message = {'message': "Authenticate."}
    resp = jsonify(message)
    resp.status_code = 401
    resp.headers['WWW-Authenticate'] = 'Basic realm="Main"'

    return resp


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
@app.route("/" , methods=['GET'])
@app.route("/login" , methods=['GET'])
def loginPage():
    return render_template("login.html")

# Register page
@app.route("/register" , methods=['GET'])
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




### API-Handler ###

@app.route("/loginAPI", methods=['POST'])
@requires_authorization
def loginAPI():

    print(request.authorization.username)
    test = request

    return simplejson.dumps("okay")  

@app.route("/registerAPI", methods=['POST'])
def registerAPI():
    json = request.json

    return "okay"

if __name__ == '__main__':
    app.run(host= '0.0.0.0')
