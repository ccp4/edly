# import importlib as imp
from subprocess import check_output,Popen,PIPE
import json,tifffile,mrcfile,os,sys,glob,time,datetime,crystals,re #,base64,hashlib
from flask import Flask,Blueprint,request,url_for,redirect,jsonify,session,render_template
from functools import wraps
import numpy as np,pandas as pd
from EDutils import utilities as ut             #;imp.reload(ut)
# from EDutils import felix as fe                 #;imp.reload(fe)
from utils import displayStandards as dsp
from utils import glob_colors as colors
import plotly.express as px
import plotly.graph_objects as go
from blochwave import bloch
from blochwave import bloch_pp as bl            #;imp.reload(bl)
from in_out import*
app = Blueprint('app', __name__)

dsp.plt.switch_backend('agg')
# felix_data = {}
# pets_data = {}


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        # print(session.get('logged_in'))
        if session.get('logged_in')==True:
            return f(*args, **kwargs)
        else:
            # flash("You need to login first")
            return redirect(url_for('login'))
    return wrap



######################################################
#### Structure related
######################################################
@app.route('/upload_cif', methods=['POST'])
def upload_cif():
    try:
        f = request.files['file_cif']
        cif_file=os.path.join(session['path'],f.filename)
        f.save(cif_file)
        return 'ok'
    except Exception as e:
        msg='could not import cif file:'
        print(colors.red+msg)
        print(colors.magenta,e,colors.black)
        return "%s : %s" %(msg, e.__str__())


@app.route('/new_structure', methods=['POST'])
def new_structure():
    data = request.form
    mol = data['name']
    val = data['val']

    path=mol_path(mol)
    cif_file=os.path.join(path,data[val])
    if val=='cif':cif_file+='.cif'
    elif val=='pdb':cif_file+='.pdb'
    # elif val=='file':cif_file.replace('.cif','.struct.cif')

    msg = 'cif file issue'
    if not mol :#or mol=="new":
        msg='Choose a proper name for the structure'
    else:
        if not os.path.exists(path):
            try:
                check_output('mkdir %s' %path,shell=True)
                if   val=='cif' :
                    crys = crystals.Crystal.from_database(data['cif'])
                    ut.crys2felix(crys,opt='w',out=cif_file)
                    cif_file=data[val]
                elif val=='pdb' :
                    crys = crystals.Crystal.from_pdb(data['pdb'],download_dir='.')
                    check_output('mv pdb%s.ent %s' %(data['pdb'],cif_file),shell=True)
                elif val=='file':
                    cif_path=os.path.join(session['path'],data['file'])
                    if os.path.exists(cif_path):
                        check_output('cp %s %s' %(cif_path,cif_file),shell=True)

                #check sucessful import
                if cif_file:
                    session['mol']=mol
                    init_mol()
                    msg='ok'
            except Exception as e:
                check_output('rm -rf %s' %path,shell=True)
                raise Exception(e)
                msg=e.__str__()
        else:
            msg='%s already exists' %mol
    print(msg)
    return msg

@app.route('/set_structure', methods=['POST'])
def set_structure():
    data = request.form
    # data=json.loads(request.data.decode())
    # print(data)
    session['mol']=data['mol']
    init_mol()
    return session['mol']


################################################
#### frame
################################################
@app.route('/get_frame', methods=['POST'])
def get_frame():
    data=json.loads(request.data.decode())
    zmax  = data['zmax']
    frame = int(data['frame'])
    exp_img,sim_img = ['static/images/dummy.png']*2
    if session['dat']['sim']:
        sim_img = get_img_frame(frame,zmax['sim'],'sim')
    if session['dat']['exp']:
        exp_img = get_img_frame(frame,zmax['exp'],'exp')
    session['frame']=frame  #;print(frame)
    return json.dumps({'exp':exp_img,'sim':sim_img})

@app.route('/update_zmax', methods=['POST'])
def update_zmax():
    data=json.loads(request.data.decode())
    img=get_img_frame(session['frame'],data['zmax'],data['key'])
    session['zm_counter']+=1
    return img

@app.route('/update_keyval', methods=['POST'])
def update_keyval():
    form = json.loads(request.data.decode())
    # print(form)
    session[form['key']]=form['val']
    # print(colors.red,form['key'],session[form['key']],colors.black)
    session['last_time']=time.time()
    return json.dumps({'key':form['key'],'val':session[form['key']]})



########################
#### structure related
########################
@app.route('/set_mode', methods=['POST'])
def set_mode():
    data = request.data.decode() #json.loads(request.data.decode())
    session['mode'] = data
    print(colors.red+session['mode']+colors.black)
    return session['mode']



############################################################################
#### Init
############################################################################
@login_required
@app.route('/init', methods=['GET'])
def init():
    now = time.time()
    print('username : ' ,session['username'])
    days = 7
    if session.get('id') and os.path.exists(session.get('path')):
        session['new'] = False
        if (now-session['last_time'])>days*24*3600:
            clear_session()
            session['new'] = True
    else:
        init_session()
        session['new'] = True
    init_mol()


    ####### package info
    if session['mode']=='felix' and not session['dat']['felix']:
        session['mode'] = 'bloch'
    if session['dat']['exp'] :
        if session['frame']>session['exp']['max_frame']:
            session['frame']=1

    info=['mol','dat','frame','crys','cif_file','mode',
        'offset','reload']
    session_data = {k:session[k] for k in info}
    # frames : exp,sim
    session_data['zmax'] = {}
    session_data['max_frame'] = 0
    if session['sim']:
        session_data['max_frame']   = session['sim']['max_frame']
        session_data['zmax']['sim'] = session['sim']['zmax']
    if session['exp']:
        session_data['max_frame']   = max(session['exp']['max_frame'],session_data['max_frame'])
        session_data['zmax']['exp'] = session['exp']['zmax']
    # print(session_data['max_frame'])
    # session_data['structures'] = [s for s in structures if s!=session['mol']]
    # session_data['gifs'] = gifs
    return json.dumps(session_data)


def clear_session():
    print('warning:tmp directory %s not used since %d days. Removing content ...' %(session.get('path'),days))
    print(check_output('rm -rf %s/*' %session.get('path'),shell=True).decode())
    # init_args()
    print(colors.red+'init0'+colors.black)

def init_session():
    id = '%s_%s' %(session['username'],create_id())
    session_path=os.path.join('static','data','tmp',id)
    print(check_output('mkdir -p %s' %session_path,shell=True).decode())
    print(colors.green+'creating new session %s' %id+colors.black)

    session['path'] = session_path
    session['id']   = id
    session['mol']  = 'silicon'
    session['mode']   = 'bloch'
    session['reload'] = False
    session['b0_path'] = get_pkl(session['id'])
    print(colors.red+'init_session'+colors.black)


def init_mol():
    # print(colors.red+'init_mol'+colors.black)
    mol = session['mol']
    exp = get_frames(mol,'exp')
    sim = get_frames(mol,'sim')
    dat = {
        'exp':type(exp)==dict,
        'sim':type(sim)==dict,
        'pets':os.path.exists(os.path.join(mol_path(mol),'pets')),
        'felix':os.path.exists(os.path.join(mol_path(mol),'felix')),
        }
    # if not os.path.exists(session['b0_path']) or new:
    struct_files = glob.glob(os.path.join(mol_path(mol),'*.cif'))
    if len(struct_files):
        struct_file=struct_files[0]
        base_file = os.path.basename(struct_file)[:-4]
        ##crystals library is rubbish as saved cif messes up the symmetry
        if base_file in crystals.Crystal.builtins:struct_file=base_file
    else:
        struct_file = glob.glob(os.path.join(mol_path(mol),'*.pdb'))[0]
    # elif os.path.basename(struct_file)[-3:]=='pdb':
    # print(struct_file)


    b0=bloch.Bloch(struct_file,path=session['path'],name='b',solve=False)
    # b0=ut.load_pkl(session['b0_path'])

    crys,cif_file=b0.crys,b0.cif_file
    crys_dat = {'file':os.path.basename(cif_file)}
    crys_dat.update({k:b_str(crys.__dict__[k],2) for k in ['a1', 'a2', 'a3']})
    crys_dat.update(dict(zip(['a','b','c','alpha','beta','gamma'],
        b_str(crys.lattice_parameters,2).split(',') )))
    crys_dat['chemical_formula'] = crys.chemical_formula
    print(crys.chemical_formula)

    if not session.get('modes'):session['modes']={'analysis':'bloch'}
    session['modes']['manual'] = not dat['pets']
    if not session.get('frame'):session['frame'] = 1
    if not session.get('offset'):session['offset'] = 0

    now = time.time()
    session['cif_file'] = cif_file
    session['crys']     = crys_dat
    session['dat'] = dat
    session['sim'] = sim
    session['exp'] = exp
    session['zm_counter'] = 0 #dummy variable
    session['last_time']  = now
    session['time']       = now


def get_frames(mol,dat):
    frames_dict=None
    frames = glob.glob(get_path(mol,dat,'*'))
    if len(frames)==0:
        return
    fmt,i = '',0
    while fmt not in fmts:
        fmt = frames[i].split('.')[-1]
        i+=1
    print(colors.red+'format found %s' %fmt+colors.black)
    # print(colors.red,get_path(mol,dat,'*'),colors.black)
    if fmt:
        frames = glob.glob(get_path(mol,dat,'*.%s' %fmt))
        max_frame=len(frames)
        min_pad = int(np.ceil(np.log10(max_frame)))
        frame0=os.path.basename(frames[0]).replace('.'+fmt,'')
        frame_str = re.findall("[0-9]{%d,}" %min_pad,frame0)[0]
        prefix = frame0.replace(frame_str,'')
        pad = len(frame_str)
        # print(frame0,frame_str,pad,prefix)
        frames_dict = {
            'tmp':0,'zmax':50, 'z_max':[50]*max_frame,
            'max_frame':max_frame,'pad':pad,'fmt':fmt,
            'prefix':prefix,
        }
        # frames_dict.update(d)
    return frames_dict

fmts = ['mrc','tiff']
def tiff_reader(tiff_file)  :
    with open(tiff_file,'rb') as f:
        I =tifffile.imread(f)
    return I
def mrc_reader(mrc_file):
    with mrcfile.open(mrc_file) as mrc:
        return mrc.data
img_readers = {
    'mrc' : mrc_reader,
    'tiff': tiff_reader,
}

def get_img_frame(frame,zmax,key):
    session['modes']['analysis']='frames'
    offset = ''
    if key=='sim':
        frame=min(max(1,frame-session['offset']),session['sim']['max_frame'])
        offset='(%d frames offset )' %session['offset']
    frame_str=str(frame).zfill(session[key]['pad'])
    png_file=png_path(session['path'],'%s_%s' %(key,frame_str))
    # print(colors.red,'reload:',session['reload'],colors.black)
    if session['reload'] or not os.path.exists(png_file) or not zmax==session[key]['z_max'][frame-1]:
        img_file = get_path(session['mol'],key,
            '%s%s.%s' %(session[key]['prefix'],frame_str,session[key]['fmt']))
        fmt = img_file.split('.')[-1]
        print(img_file)
        im = img_readers[fmt](img_file)

        dsp.stddisp(im=[im],caxis=[0,zmax],cmap='viridis',
            figsize=(10,)*2,
            pOpt="p", axPos=[0.05,0.05,0.9,0.9],
            name=png_file,title='frame %s %s' %(frame_str,offset),
            opt='sc')
        dsp.plt.close()

        session[key]['zmax'] = zmax
        session[key]['z_max'][frame-1] = zmax

    ##### Dirty fix for automatic reload
    # The image is stored as `png_file`. It is copied and sent back
    # to angularJS as `new_tmp` to force reloading
    tmp=session[key]['tmp']
    old_tmp=png_path(session['path'],'tmp_%s_%d' %(key,tmp))
    new_tmp=png_path(session['path'],'tmp_%s_%d' %(key,tmp+1))
    if os.path.exists(old_tmp):
        p=Popen('rm %s' %(old_tmp),shell=True,stdout=PIPE,stderr=PIPE)
    p=Popen('cp %s %s' %(png_file,new_tmp),shell=True,stdout=PIPE,stderr=PIPE)
    o,e=p.communicate()
    if e:print(e.decode())
    session[key]['tmp']+=1
    # print(session[key]['tmp'])
    return new_tmp
