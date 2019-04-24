# vv import Area

from flask import Flask, request, render_template, redirect
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

# vv login
@app.route("/" , methods=['GET'])
def main():
    return render_template("login.html")

@app.route("/login", methods=['POST'])
def login():
    if(request.form['email'] == "test@quatsch.de"):
        return redirect("/index")
    else:
        return redirect("/")


# ^^ login

# vv index
@app.route("/index", methods=["GET"])
def index():
    return render_template("index.html")

# ^^ index




## ------------vv api

@app.route("/loginAPI", methods=['POST'])
def loginAPI():

    json = request.json

    return "okay"

@app.route("/registerAPI", methods=['POST'])
    json = request.json

    return "okay"


## ------------^^ api


if __name__ == '__main__':
    app.run()
