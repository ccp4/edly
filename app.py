import importlib as imp
from subprocess import check_output,Popen,PIPE
import json,os,sys,glob,time,datetime,crystals,re #,base64,hashlib
import tifffile,mrcfile,cbf
from flask import Flask,Blueprint,request,url_for,redirect,jsonify,session,render_template
from functools import wraps
import numpy as np,pandas as pd
from EDutils import utilities as ut                 #;imp.reload(ut)
from EDutils import readers                         #;imp.reload(readers)
# from EDutils import felix as fe                   #;imp.reload(fe)
from utils import displayStandards as dsp
from utils import glob_colors as colors
import plotly.express as px
import plotly.graph_objects as go
from blochwave import bloch
from blochwave import bloch_pp as bl                #;imp.reload(bl)
from in_out import*
app = Blueprint('app', __name__)
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        # print(session.get('logged_in'))
        if session.get('logged_in')==True:
            return f(*args, **kwargs)
        else:
            # flash("You need to login first")
            return redirect(url_for('login'))
# records=ut.load_pkl('static/spg/records.pkl')

######################################################
#### import related
######################################################

@app.route('/get_dl_state', methods=['GET'])
def get_dl_state():
    log_file="%s/dl.log" %(session['path'])
    cmd=r"grep '%%'  %s" %log_file
    cmd+=r" | tail -n1 | sed -rE 's/([0-9]*%%)/;\1;/g' | cut -d';' -f2"
    dl_state=check_output(cmd,shell=True).decode().strip()
    msg='Download state : \n%s\n' %dl_state
    if dl_state=="100%":
        cmd = 'tail -n1 %s' %os.path.realpath("%s/uncompress.log" %session['path'])
        file_extract=check_output(cmd,shell=True).decode().strip()
        msg='Extracting : \n%s\n' %file_extract
    return msg

@app.route('/download_frames', methods=['POST'])
def download_frames():
    link = request.data.decode()
    job  = r'''#!/bin/bash
#auto generated download and uncompress job script

if [ ! -d {filepath} ];then
    mkdir -p {filepath}
fi
cd {filepath}
wget -o {log_path} -O {filename} {link}
{uncompress_cmd} {filename} > {cmd_log}
rm {filename}
    '''.format(
        filepath        = os.path.realpath(data_path(link)),
        log_path        = os.path.realpath("%s/dl.log" %session['path']),
        link            = link.replace('?download=1',''),
        filename        = os.path.basename(link.replace('?download=1','')),
        uncompress_cmd  = uncompress_fmts[get_compressed_fmt(link)],
        cmd_log         = os.path.realpath("%s/uncompress.log" %session['path']),
    )#;print(job)

    job_file="%s/dl.sh" %(session['path'])      #;print(job_file)
    with open(job_file,'w') as f :
        f.write(job)

    cmd = 'bash %s' %job_file
    out=check_output(cmd,shell=True).decode().strip()#;print(out)
    return out

@app.route('/import_frames', methods=['POST'])
def import_frames():
    link=request.data.decode()
    fmt=get_compressed_fmt(link)
    if fmt not in compress_fmts:
        msg='Compressed file should be of the following formats :\n %s' %(','.join(compress_fmts))
    else:
        msg='ready to download'
    return json.dumps({'msg':msg})

@app.route('/check_dl_frames', methods=['POST'])
def check_dl_frames():
    link     = request.data.decode()
    filepath = data_path(link)                #;print(filepath)
    dl       = os.path.exists(data_path(link))
    folders  = []
    if dl:
        cmd=r'cd {path};for dir in `find {folder} -type d`;do for fmt in img cbf smv tiff;do find $dir -maxdepth 1 -type f -name "*.$fmt" -not -name ".*" | head -n1;done;done'.format(
            path    = 'static/database',
            folder  = os.path.basename(filepath),
        )
        # print(cmd)
        files = check_output(cmd,shell=True).decode().strip()
        folders = [os.path.dirname(f) for f in files.split('\n')]
        # print(files,folders)
    return json.dumps({'dl':dl,'folders':folders})

@app.route('/create_sym_link', methods=['POST'])
def create_sym_link():
    folder = request.data.decode()  #;print(folder)
    cmd='if [ -L {exp_path} ];then rm {exp_path};fi;ln -s {folder} {exp_path}'.format(
        folder   =os.path.realpath('static/database/%s' %folder),
        exp_path = os.path.join(mol_path(session['mol']),'exp')
        )
    # print(cmd)
    out=check_output(cmd,shell=True).decode().strip()    #;print(out)
    session['exp'] = init_frames(session['mol'],'exp')
    session['dat']['exp']=True
    return json.dumps({'dat':session['dat'],
        'nb_frames':session['exp']['nb_frames'],
        'folder':session['exp']['folder'],
        })




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

@app.route('/set_mode', methods=['POST'])
def set_mode():
    data = request.data.decode() #json.loads(request.data.decode())
    session['mode'] = data
    # print(colors.red+session['mode']+colors.black)
    return session['mode']

def get_structure_file():
    '''reading priorities:
    - built-in
    - cif
    - pdb
    '''
    struct_file=''
    mol = session['mol']
    if mol in crystals.Crystal.builtins:
        struct_file=mol
    else:
        cif_files = glob.glob(os.path.join(mol_path(mol),'*.cif'))
        if len(cif_files):
            struct_file=cif_files[0]
            base_file = os.path.basename(struct_file)[:-4]
            ##crystals library is rubbish as saved cif messes up the symmetry
        else:
            pdb_files = glob.glob(os.path.join(mol_path(mol),'*.pdb'))
            if len(pdb_files):
                struct_file = pdb_files[0]
    return struct_file

################################################
#### frames related
################################################
@app.route('/get_frame', methods=['POST'])
def get_frame():
    data=json.loads(request.data.decode())
    return json.dumps(get_frame_img(int(data['frame']),data['type']).tolist() )

@app.route('/update_keyval', methods=['POST'])
def update_keyval():
    form = json.loads(request.data.decode())
    # print(form)
    session[form['key']]=form['val']
    # print(colors.red,form['key'],session[form['key']],colors.black)
    session['last_time']=time.time()
    return json.dumps({'key':form['key'],'val':session[form['key']]})

def get_frame_img(frame,key):
    offset = ''
    if key=='sim':
        frame=min(max(0,frame-session['offset']),session['sim']['nb_frames']-1)
        offset='(%d frames offset )' %session['offset']
    else:
        frame=min(max(0,frame),session['exp']['nb_frames']-1)
    # frame_str=str(frame+session[key]['min_frame']).zfill(session[key]['pad'])
    # print(session[key]['pad'],frame,session[key]['min_frame'],frame_str)
    # img_file = get_path(session['mol'],key,
    #     '%s%s.%s' %(session[key]['prefix'],frame_str,session[key]['fmt']))
    img_path = get_path(session['mol'],key,'*.%s' %session[key]['fmt'])
    img_file = np.sort(glob.glob(img_path))[frame]  #;print(img_file)
    fmt = img_file.split('.')[-1]
    im = readers.read(img_file)
    wh = im.shape[0]
    step=1
    if wh>512:
        step = wh//512#int(np.ceil())
        im = im[::step,::step]
    min_v = 0#im.mean()
    scale = 1#3000/im.max()
    im = np.maximum(im.flatten()-min_v,0)*scale
    # print(min_v,scale)
    img = np.array(im,dtype=int)
    return img



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
        if (now-session.get('last_time'))>days*24*3600:
            clear_session()
            session['new'] = True
            init_session()
    else:
        init_session()
        session['new'] = True

    #### Done at every init
    init_mol()

    ### get zenodo records
    # records_d=records.title.to_dict()
    # json_records=json.dumps(dict(zip(records_d.values(),records.keys())

    ####sanity checks
    if session['mode']=='felix' and not session['dat']['felix']:
        session['mode'] = 'bloch'
    if session['dat']['exp'] :
        if session['frame']>session['nb_frames']:
            session['frame']=1

    ####### package info to frontend
    info=['mol','dat','frame','crys','mode','zmax','nb_frames',
        'offset','cmap','cmaps','heatmaps','nb_colors',
        'new','b0_path',]
    session_data = {k:session[k] for k in info}
    folder=''
    if session['dat']['exp']:
        folder=session['exp']['folder']
    session_data['folder']=folder
    session['init'] = True
    # print(colors.magenta+'init done : ',session['init'],colors.black)

    # print(session_data['max_frame'])
    # session_data['structures'] = [s for s in structures if s!=session['mol']]
    # session_data['gifs'] = gifs
    return json.dumps(session_data)

def init_session():
    id = '%s_%s' %(session['username'],create_id())
    session_path=os.path.join('static','data','tmp',id)
    print(check_output('mkdir -p %s' %session_path,shell=True).decode())
    print(colors.green+'creating new session %s' %id+colors.black)

    session['path'] = session_path
    session['id']   = id
    session['mol']  = 'GaAs'
    session['mode'] = 'bloch'
    session['viewer_molecule'] = False;


    # session['reload']  = False
    session['b0_path'] = get_pkl(session['id'])
    # print(colors.red+'init_session'+colors.black)
    #colormaps
    session['zmax']      = dict(zip(['sim','exp'],[50]*2))
    session['nb_colors'] = 100
    session['cmap']      = 'hot'
    session['cmaps']     = ['hot','viridis','Greys_r','Spectral']
    session['heatmaps']  = {k:np.array(255 * np.array(dsp.getCs(k, session['nb_colors'])).flatten(), dtype=np.uint8).tolist()
        for k in session['cmaps']}

def init_mol():
    # print(colors.red+'init_mol'+colors.black)
    mol = session['mol']
    sim = init_frames(mol,'sim')
    exp = init_frames(mol,'exp')
    dat_type=update_exp_data(mol)
    dat = {
        'exp'       : type(exp)==dict,
        'sim'       : type(sim)==dict,
        'pets'      : type(dat_type)==str,
        'dat_type'  : dat_type,
        'felix'     : os.path.exists(os.path.join(mol_path(mol),'felix')),
        'rock'      : False,
        'omega'     : 0,
        }

    # get the max number of frames for frontend from frames simulated/experimental frames
    # or processed data.
    # Note : sometimes processed datasets may have discarded experimental frames
    # so only keep those ones then
    nb_frames = 0
    if dat['sim']:
        nb_frames = sim['nb_frames']
    if dat['exp']:
        nb_frames = max(exp['nb_frames'],nb_frames)
    if dat['pets']:
        dat['rock'] = dat_type=='pets'
        pets = pets_data[mol]
        pets_frames = pets.uvw0.shape[0]
        if nb_frames:
            nb_frames = min(pets_frames,nb_frames)
        else:
            nb_frames = pets_frames
        # if 'omega' in pets.__dict__:
        #     ###will have to fix this later
        #     if mol=='glycine':pets.omega=157
        #     dat['omega']=pets.omega
        #     # print("omega=%.1fdeg information found in exp data " %dat['omega'])

    ## initialize structure
    struct_file = get_structure_file()
    if struct_file:
        b0=bloch.Bloch(struct_file,path=session['path'],name='b',solve=False)
        print('saving bloch object')
        b0.save()
        # b0=ut.load_pkl(session['b0_path'])

        crys,cif_file=b0.crys,b0.cif_file
        crys_dat = {'file':os.path.basename(cif_file),'cif_file':cif_file}
        crys_dat.update({k:b_str(crys.__dict__[k],2) for k in ['a1', 'a2', 'a3']})
        crys_dat.update(dict(zip(['a','b','c','alpha','beta','gamma'],
            b_str(crys.lattice_parameters,2).split(',') )))
        formula = re.sub("([0-9]+)", r"_{\1}", crys.chemical_formula).replace(' ','')
        crys_dat['chemical_formula'] = formula
        crys_dat['lattice_system']=crys.lattice_system.name
        crys_dat['nb_atoms']=len(crys.atoms)
        crys_dat['spg_ref']=False
        ### space group stuff
        dataset = ut.read_space_group(struct_file)  #;print(dataset)
        if not dataset:
            try :
                dataset = crys.symmetry()
            except:
                dataset={}
                print(colors.red+'Crystal.symmetry() failed'+colors.black)
        crys_dat['spg']=all([k in dataset.keys() for k in
            ['international_number','international_symbol']])
        if crys_dat['spg']:
            crys_dat.update({k:dataset[k] for k in['international_number','international_symbol']})
            crys_dat['spg_ref'] = 'http://img.chem.ucl.ac.uk/sgp/large/%s%s.htm' %(
                str(crys_dat['international_number']).zfill(3),
                ['az1','ay1'][crys.lattice_system.name=='monoclinic']
            )
            if 'lattice_system' in dataset.keys():crys_dat['lattice_system'] = dataset['lattice_system']
    else:
        crys_dat=dict(zip(
        ['file','a','b','c','alpha','beta','gamma','a1', 'a2', 'a3','chemical_formula',
            'nb_atoms','lattice_system'],
        ['?']*13))
        crys_dat['spg_ref']=False
    # print(crys_dat)
    # print(formula)

    #related to /set_viewer
    if session.get('bloch_modes'):
        # print('mol init :',session['bloch_modes'])
        if session['bloch_modes']['u0']=='auto' and not dat['pets']:
            session['bloch_modes']['u0'] = 'edit'
    if not session.get('frame') :session['frame']  = 1
    if not session.get('offset'):session['offset'] = 0

    now = time.time()
    # session['cif_file'] = struct_file
    session['crys']       = crys_dat
    session['dat']        = dat
    session['sim']        = sim
    session['exp']        = exp
    session['nb_frames']  = nb_frames
    session['last_time']  = now
    session['time']       = now

def init_frames(mol,frame_type):
    frame_path  = os.path.join(mol_path(mol),frame_type)
    frames_dict = readers.detect_frame(frame_path)
    if frames_dict:
        print(colors.green+'format detected for %s frames :' %frame_type, end="")
        print(colors.yellow,'%s (%d)' %(frames_dict['fmt'],frames_dict['nb_frames']) ,colors.black)
        cmd = "basename `readlink %s`" %frame_path
        frames_dict['folder'] = check_output(cmd,shell=True).decode().strip()
    return frames_dict

def clear_session():
    print('warning:tmp directory %s not used since %d days. Removing content ...' %(session.get('path'),days))
    print(check_output('rm -rf %s/*' %session.get('path'),shell=True).decode())
    # init_args()
    print(colors.red+'init0'+colors.black)
