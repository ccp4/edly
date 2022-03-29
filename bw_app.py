from flask import Flask,Blueprint,request,jsonify,session,render_template
from subprocess import check_output,Popen,PIPE
import json,tifffile,os,sys,glob,time,datetime #,base64,hashlib
import numpy as np
from blochwave import bloch
from EDutils import utilities as ut
from utils import displayStandards as dsp
from utils import glob_colors as colors
import plotly.express as px
from string import ascii_letters,digits
bw_app = Blueprint('bw_app', __name__)

mol_path=lambda mol:'static/data/%s' %mol
exp_path=lambda mol,frame_str:os.path.join(mol_path(mol),'pets','tiff','%s.tiff' %frame_str)
png_path=lambda path,frame_str:os.path.join(path,'%s.png' %frame_str)
tmp_path=lambda path,tmp:os.path.join(path,'%d.png' %tmp)
chars = ascii_letters+digits
# hashme=lambda id: base64.b64encode(hashlib.sha256(("%d" %id).encode("UTF-8")).digest()).decode()

@bw_app.route('/')
def image_viewer():
    return render_template('bloch.html')#,config=config)

@bw_app.route('/get_frame', methods=['POST'])
def get_frame():
    data=json.loads(request.data.decode())
    # print('fetching frame')
    frame = int(data['frame'])
    zmax  = data['zmax']
    frame_str=str(frame).zfill(session['pad'])
    png_file=png_path(session['tmp_path'],frame_str)
    if not os.path.exists(png_file) or not zmax==session['z_max'][frame]:
        tiff_file=exp_path(session['mol'],frame_str)
        im = tifffile.imread(tiff_file)
        session['zmax'] = zmax
        session['z_max'][frame] = zmax
        dsp.stddisp(im=[im],caxis=[0,zmax],cmap='viridis',pOpt='im',
            name=png_file,title='frame %s' %frame_str, opt='sc')
    old_tmp=tmp_path(session['tmp_path'],session['tmp'])
    session['tmp']+=1
    new_tmp=tmp_path(session['tmp_path'],session['tmp'])
    print(check_output('rm %s;cp %s %s' %(old_tmp,png_file,new_tmp),shell=True).decode())
    png_file = new_tmp
    session['frame']=frame
    # print('finished')
    return json.dumps({'png_file':png_file})



@bw_app.route('/solve_bloch', methods=['POST'])
def solve_bloch():
    # keV =  float(request.form['keV'])
    # theta,phi = np.array([request.form['theta'],request.form['phi']],dtype=float)
    # Smax,Nmax = float(request.form['Smax']),int(request.form['Nmax'])
    # thick = float(request.form['thick'])
    # thick=100
    # print(keV,theta,phi,Nmax,Smax,thick)

    # u = ut.u_from_theta_phi(theta,phi)
    # b0 = bloch.Bloch('diamond',path='dat/',keV=keV,u=u,Nmax=Nmax,Smax=Smax,
    #     opts='svt',thick=thick)

    b0 = bloch.Bloch('diamond',path='dat/',keV=200,u=[1,0,1],Nmax=5,Smax=0.1,
        opts='svt',thick=10)
    b0.df_G['I']*=100
    b0.df_G['Vga']*=100
    toplot=b0.df_G[['px','py','I','Vga']]
    # fig=px.scatter(b0.df_G,x='px',y='py',size='I',)
    toplot=toplot.melt(value_vars=['I','Vga'],id_vars=['px','py'])
    fig=px.scatter(toplot,x='px',y='py',color='variable',size='value')
    data = fig.to_json()
    return data


@bw_app.route('/init', methods=['GET'])
def init():
    now = time.time()
    try :
        session_id=session.get('session_id')
        if (now-session['last_time'])>24*3600:
            print(check_output('rm %s/*' %session['tmp_path'],shell=True).decode())
    except Exception as e:
        print(e)
        id=''.join([chars[s] for s in np.random.randint(0,len(chars),10)])
        mol='glycine'
        frames = glob.glob(exp_path(mol,'*'))
        max_frame=len(frames)
        session_path=os.path.join('static','data','tmp',id)

        session['id']    = id
        session['frame'] = 1
        session['mol']   = mol
        session['tmp']   = 0
        session['zmax']  = 100
        session['max_frame']= max_frame
        session['pad']      = len(os.path.basename(frames[0]).replace('.tiff',''))
        session['z_max']    = [100]*max_frame
        session['tmp_path'] = session_path
        # if not os.path.exists(session_path):
        print(check_output('mkdir -p %s' %session_path,shell=True).decode())

    session['last_time']=now
    return json.dumps({k:session[k] for k in ['mol','max_frame','zmax','frame'] })
