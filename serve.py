#! .env/bin/python3
from flask import Flask
from app import app
from felix import felix
from bloch import bloch
from login import login

main_app = Flask(__name__)
main_app.secret_key = b'_5#y2L"F4Q8z\n\xfc]/'

main_app.register_blueprint(login)
main_app.register_blueprint(app)
main_app.register_blueprint(felix)
main_app.register_blueprint(bloch)

if __name__ == "__main__":
    main_app.run(host='0.0.0.0',port=8020)
