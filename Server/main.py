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

### Handler ###

# Login handler
@app.route("/doLogin", methods=['POST'])
def doLogin():
    if(request.form['email'] == "test@quatsch.de"):
        return redirect("/index")
    else:
        return redirect("/")


# Run start
if __name__ == '__main__':
    app.run()
