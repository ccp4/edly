#! .env/bin/python3
from flask import Flask
from bw_app import bw_app
from felix import felix
from bloch import bloch
from login import login

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xfc]/'

app.register_blueprint(bw_app)
app.register_blueprint(felix)
app.register_blueprint(bloch)
app.register_blueprint(login)

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=8020)
