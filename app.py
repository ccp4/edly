from flask import render_template
from flask import Flask,request,jsonify
from subprocess import Popen,PIPE
import json,tifffile,os,sys
import numpy as np,glob
from blochwave import bloch
from EDutils import utilities as ut
from utils import displayStandards as dsp
from utils import glob_colors as colors

app = Flask(__name__)
path='/' #'file://'+os.path.realpath(os.path.dirname(__file__))
frame='1'
im_w=700
config={'frame':frame,'im_w':'%d' %im_w}

@app.route('/')
def image_viewer():
    # png_file=make_png(frame)
    # config['png_file']=png_file
    return render_template('image_viewer.html')#,config=config)

@app.route('/solve_bloch', methods=['POST'])
def solve_bloch():
    keV =  float(request.form['keV'])
    theta,phi = np.array([request.form['theta'],request.form['phi']],dtype=float)
    Smax,Nmax = float(request.form['Smax']),int(request.form['Nmax'])
    thick = float(request.form['thick'])
    # thick=100
    print(keV,theta,phi,Nmax,Smax,thick)

    u = ut.u_from_theta_phi(theta,phi)
    b0 = bloch.Bloch('diamond',path='dat/',keV=keV,u=u,Nmax=Nmax,Smax=Smax,
        opts='svt',thick=thick)

    data={'params':[keV,theta,phi,Nmax,Smax,thick,b0.gammaj.shape[0] ]}
    data.update({'gamma':list(b0.gammaj)})
    return json.dumps(data)#jsonify(data)



@app.route('/update_frame', methods=['POST'])
def update_frame():
    frame =  request.form['frame']
    # src=make_png(frame)
    # return json.dumps({'src':png_file})
    src='static/png/%s.png' %frame.zfill(5)
    http_img="<a class='container' href=%s><img src=%s id='frame_img' width='%d' ></a>" %(src,src,im_w)
    return http_img


def make_png(frame):
    frame_str=frame.zfill(5)
    png_file='static/png/%s.png' %frame_str
    im=tifffile.imread('static/tiff/%s.tiff' %frame_str)
    dsp.stddisp(im=[im],caxis=[0,100],cmap='viridis',pOpt='im',
        name=png_file,opt='sc')
    return os.path.join(path,png_file)

if __name__ == "__main__":
    tiff_folder='static/tiff/'
    png_folder='static/png/'
    if not os.path.exists(tiff_folder) :
        print(colors.red+'warning : put the tiff directory in static/ first : \n ln -s <your_tiff_folder_location> static/tiff'+colors.black)
        sys.exit()
    if not os.path.exists(png_folder) :
        print(colors.blue+'creating directory static/png'+colors.black)
        p=Popen('mkdir %s' %png_folder, shell=True)

    tiff_files=glob.glob(os.path.join(tiff_folder,'*.tiff'))
    png_files=glob.glob(os.path.join(png_folder,'*.png'))
    if not len(tiff_files)==len(png_files):
        tiff_f = np.array([os.path.basename(f).split('.')[0] for f in tiff_files],dtype=int)
        png_f  = np.array([os.path.basename(f).split('.')[0] for f in png_files],dtype=int)
        frames = np.setdiff1d(tiff_f,png_f)
        print(colors.blue + 'generating png for missing frames : '+colors.black, frames)
        for f in frames:make_png(str(f))

    app.run(host='0.0.0.0',port=8050)
    # print(make_png(frame))
