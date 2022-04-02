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
get_path=lambda mol,key,frame_str:os.path.join(mol_path(mol),key,'%s.tiff' %frame_str)
png_path=lambda path,frame_str:os.path.join(path,'%s.png' %frame_str)
# tmp_path=lambda path,tmp:os.path.join(path,'%d.png' %tmp)
chars = ascii_letters+digits

@bw_app.route('/')
def image_viewer():
    return render_template('bloch.html')

@bw_app.route('/get_frame', methods=['POST'])
def get_frame():
    data=json.loads(request.data.decode())
    frame = int(data['frame'])
    zmax  = data['zmax']
    exp_img = get_img_frame(frame,zmax['exp'],'exp')
    sim_img = get_img_frame(frame,zmax['sim'],'sim')
    session['frame']=frame
    return json.dumps({'exp':exp_img,'sim':sim_img})

@bw_app.route('/update_zmax', methods=['POST'])
def update_zmax():
    data=json.loads(request.data.decode())
    img=get_img_frame(session['frame'],data['zmax'],data['key'])
    session['zm_counter']+=1
    return img

def get_img_frame(frame,zmax,key):
    session['analysis_mode']=False
    if key=='sim':
        frame=min(max(1,frame-session['sim']['offset']),session['sim']['max_frame'])
    frame_str=str(frame).zfill(session[key]['pad'])
    png_file=png_path(session['path'],'%s_%s' %(key,frame_str))
    if not os.path.exists(png_file) or not zmax==session[key]['z_max'][frame-1]:
        tiff_file=get_path(session['mol'],key,frame_str)
        im = tifffile.imread(tiff_file)
        dsp.stddisp(im=[im],caxis=[0,zmax],cmap='viridis',
            figsize=(10,)*2,
            pOpt="p", axPos=[0.05,0.05,0.9,0.9],
            name=png_file,title='frame %s' %frame_str, opt='sc')

        session[key]['zmax'] = zmax
        session[key]['z_max'][frame-1] = zmax

    ##### Dirty fix for automatic reload
    # The image is stored as `png_file`. It is copied and sent back
    # to angularJS as `new_tmp` to force reloading
    tmp=session[key]['tmp']
    old_tmp=png_path(session['path'],'tmp_%s_%d' %(key,tmp))
    new_tmp=png_path(session['path'],'tmp_%s_%d' %(key,tmp+1))
    p=Popen('rm %s;cp %s %s' %(old_tmp,png_file,new_tmp),shell=True,stdout=PIPE,stderr=PIPE)
    o,e=p.communicate()
    if e:print(e.decode())
    session[key]['tmp']+=1
    # print(session[key]['tmp'])
    return new_tmp


@bw_app.route('/solve_bloch', methods=['POST'])
def solve_bloch():
    session['analysis_mode']=True
    # keV =  float(request.form['keV'])
    # theta,phi = np.array([request.form['theta'],request.form['phi']],dtype=float)
    # Smax,Nmax = float(request.form['Smax']),int(request.form['Nmax'])
    # thick = float(request.form['thick'])
    # thick=100
    # print(keV,theta,phi,Nmax,Smax,thick)

    # u = ut.u_from_theta_phi(theta,phi)
    # b0 = bloch.Bloch('diamond',path='dat/',keV=keV,u=u,Nmax=Nmax,Smax=Smax,
    #     opts='svt',thick=thick)
    b_args = session['bloch']
    b0 = bloch.Bloch(session['cif_file'],path='dat/',**b_args)
    b0.df_G['I']   *=200
    b0.df_G['Vga'] *=200
    b0.df_G['Swa'] *=200
    toplot=b0.df_G[['px','py','I','Vga','Swa']]
    # fig=px.scatter(b0.df_G,x='px',y='py',size='I',)
    toplot=toplot.melt(value_vars=['I','Vga','Swa'],id_vars=['px','py'])
    fig=px.scatter(toplot,x='px',y='py',color='variable',size='value',
        width=780, height=780)

    fig.update_layout(
        margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor="LightSteelBlue",
    )
    data = fig.to_json()
    return data

@bw_app.route('/toggle_molecule', methods=['GET'])
def toggle_molecule():
    session['show_molecule']=not session['show_molecule']
    return json.dumps({'show_molecule':session['show_molecule']})

@bw_app.route('/set_structure', methods=['POST'])
def set_structure():
    data=json.loads(request.data.decode())
    cif_file=os.path.join(mol_path(session['mol']),'pets',data['cif'])
    session['cif'] = data['cif']
    session['cif_file'] = cif_file
    return session['cif_file']

@bw_app.route('/init', methods=['GET'])
def init():
    now = time.time()
    if session.get('id') and os.path.exists(session.get('path')):
        if (now-session['last_time'])>24*3600:
            print(check_output('rm %s/*' %session.get('path'),shell=True).decode())
    else:
        id=''.join([chars[s] for s in np.random.randint(0,len(chars),10)])
        session_path=os.path.join('static','data','tmp',id)
        print(check_output('mkdir -p %s' %session_path,shell=True).decode())

        mol='test'
        exp_frames = glob.glob(get_path(mol,'exp','*'))
        sim_frames = glob.glob(get_path(mol,'sim','*'))
        exp_max_frame=len(exp_frames)
        sim_max_frame=len(sim_frames)

        exp = {
            'tmp':0,'zmax':50, 'z_max':[50]*exp_max_frame,
            'max_frame':exp_max_frame,
            'pad':len(os.path.basename(exp_frames[0]).replace('.tiff',''))
            }
        sim = {
            'tmp':0,'zmax':100, 'z_max':[100]*sim_max_frame,
            'max_frame':sim_max_frame,
            'pad':len(os.path.basename(sim_frames[0]).replace('.tiff','')),
            'offset':10,
            }
        bloch_args={'keV':200,'u':[1,0,1],'Nmax':5,'Smax':0.1,
            'thick':10,'opts':'svt'}

        session['id']    = id
        session['path']  = session_path
        session['mol']   = mol
        session['cif']      = 'alpha_glycine.cif'
        # session['cif'] = '1ejg.pdb'
        session['cif_file'] = os.path.join(mol_path(mol),'pets',session['cif'])
        session['frame'] = 1
        session['sim']   = sim
        session['exp']   = exp
        session['analysis_mode'] = False
        session['show_molecule'] = False
        session['zm_counter'] = 0 #dummy variable
        session['bloch']      = bloch_args
        session['last_time']  = now
        # print(session['cif'],session.get('exp'+'tmp'))

    print('send init info')
    session_data = {k:session[k] for k in ['mol','frame','cif','cif_file','analysis_mode','show_molecule','bloch']}
    session_data['max_frame']=session['exp']['max_frame']
    for k in ['zmax']:
        session_data[k] = dict(zip(['sim','exp'],[session['sim'][k],session['exp'][k]]))
    return json.dumps(session_data)
