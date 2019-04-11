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
@app.route("/login", methods=['POST'])
def login():

    json = request.json

    print(json)

    return simplejson.dumps({'success': json['username'] == 'krypto' and json['password'] == 'koffer'})

    

# ^^ testArea

if __name__ == '__main__':
    app.run()
