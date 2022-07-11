from flask import Flask,Blueprint,request,url_for,redirect,jsonify,session
from flask import render_template,make_response
import crystals,glob,os,socket,json
from functools import wraps
from in_out import structures,builtins,gifs
login = Blueprint('login', __name__)
server_home='/'
if socket.gethostname()=='tarik-CCP4':server_home=''
version='0.0.5'

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

@login.route('/set_viewer',methods=['GET'])
def set_viewer():
    args = request.args
    # params = {'mol':structures,'modes':['bloch','frames']}
    # for k,v in args:
    #     if k in params.keys():
    #         if v in params[k]:session[k] = v
    if 'mol' in args.keys():
        if args['mol'] in structures:
            session['mol'] = args['mol']
    if 'mode' in args.keys():
        if args['mode'] in ['bloch','frames']:
            if not session.get('modes'):session['modes'] = {}
            session['modes']['analysis'] = args['mode']
    if 'frame' in args.keys():
        frame = json.loads(args['frame'])
        if isinstance(frame,int) :
            session['frame'] = frame
    print('set session info : ')
    print({k : session.get(k) for k in ['mol','modes','frame']})
    return redirect(server_home+url_for('login.viewer'))

# @login.route('/viewer/#/felix',methods=['GET'])
# @login.route('/viewer/#/bloch',methods=['GET'])
# @login.route('/viewer/',methods=['GET'])
@login.route('/viewer',methods=['GET'])
def viewer():
    if not session.get('logged_in'):
        print('attempt to see bloch viewer while not logged in')
        return redirect(server_home+url_for('login.home'))
    else:
        # return make_response(open('templates/main.html').read())
        return make_response(render_template('main.html',builtins=builtins,structures=structures,gifs=gifs,version=version))

@login.route('/', methods=['GET', 'POST'])
def home():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return redirect(url_for('login.viewer'))
