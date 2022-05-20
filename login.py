from flask import Flask,Blueprint,request,url_for,redirect,jsonify,session,render_template
from functools import wraps
login = Blueprint('login', __name__)

import crystals,glob,os
builtins = crystals.Crystal.builtins
gifs = {os.path.basename(s)[:-4]:s for s in glob.glob("static/gifs/*")}


@login.route('/login', methods=['GET','POST'])
def log_in():
    session['logged_in'] = False
    if request.method == 'GET':
        return render_template('login.html')
    else:
        username = request.form['username']
        # passw    = request.form['password']
        if not username:
            msg='please enter username'
        # elif not passw=="ccp4_debloch!":
        #     msg='wrong password. Contact tarik.drevon@stfc.ac.uk for access'
        else:
            session['logged_in'] = True
            session['username']  = username
            print('username : ' ,username)
            msg='ok'
        return msg

@login.route('/viewer',methods=['GET'])
def viewer():
    if not session.get('logged_in'):
        print('attempt to see bloch viewer while not logged in')
        return redirect(url_for('login.home'))
    else:
        return render_template('bloch.html',builtins=builtins,gifs=gifs)

@login.route('/', methods=['GET', 'POST'])
def home():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return redirect(url_for('login.viewer'))
