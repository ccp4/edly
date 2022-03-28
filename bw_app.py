from flask import render_template
from flask import Flask,request,jsonify,session
from subprocess import Popen,PIPE
import json,tifffile,os,sys,glob
import numpy as np,glob
from blochwave import bloch
from EDutils import utilities as ut
from utils import displayStandards as dsp
from utils import glob_colors as colors

app = Flask(__name__)
mol_path=lambda mol:'static/data/%s' %mol



@app.route('/')
def image_viewer():
    return render_template('bloch.html')#,config=config)

@app.route('/get_frame', methods=['POST'])
def get_frame():
    data=json.loads(request.data.decode())
    print('fetching frame')
    frame = data['frame']
    # frame_str=str(frame).zfill(3)
    frame_str=str(frame).zfill(5)
    tiff_file=os.path.join(mol_path(mol),'dat','pets','tiff','%s.tiff' %frame_str)
    # tiff_file=os.path.join(mol_path(mol),'sim','tiff','sum','%s.tiff' %frame_str)
    # static/data/glycine/dat/pets/tiff/
    im=tifffile.imread(tiff_file).tolist()
    print('finished')
    return json.dumps({'im':im})

@app.route('/get_info', methods=['GET'])
def get_info():
    # session['']
    max_frame=len(glob.glob(os.path.join(mol_path(mol),'exp', '*.png')))
    return json.dumps({'max_frame':max_frame})

if __name__ == "__main__":
    mol = 'glycine'
    app.run(host='0.0.0.0',port=8020)
