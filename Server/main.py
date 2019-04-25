# vv import Area

from flask import Flask, request, render_template, redirect, jsonify
import simplejson


# ^^ import Area

# vv config

app = Flask(__name__)


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


  


# vv login
@app.route("/" , methods=['GET'])
def main():
    return render_template("login.html")

@app.route("/login", methods=['POST'])
def login():
    if check_user_and_password(request.form['email'], request.form['password']):
        return render_template('index.html')
    else:
        return authenticate()


# ^^ login

# vv index
@app.route("/index", methods=["GET"])
def index():
    return render_template("index.html")

# ^^ index




## ------------vv api

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


## ------------^^ api


if __name__ == '__main__':
    app.run(host= '0.0.0.0')
