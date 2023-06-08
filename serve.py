#! .env/bin/python3
import os,sys,argparse
from flask import Flask
from app import app
from felix import felix
from bloch import bloch
from login import login

usage='''Usage:
serve.py [-p|--port=<port_nb>] [-d|--debug] [-h|--help]

OPTIONS
-------
    - port : port number (default 8020)
    - d    : debug mode (default False)
    - h    : show this help
'''
parser = argparse.ArgumentParser()
parser.add_argument('-p','--port'  ,default=8020)
parser.add_argument('-d','--debug' ,action='store_true',default=False)
args = parser.parse_args()


main_app = Flask(__name__)
main_app.secret_key = b'_5#y2L"F4Q8z\n\xfc]/'

main_app.register_blueprint(login)
main_app.register_blueprint(app)
main_app.register_blueprint(felix)
main_app.register_blueprint(bloch)


if __name__ == "__main__":
    main_app.run(host='0.0.0.0',debug=args.debug,port=args.port)
