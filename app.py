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



@app.route('/set_mode', methods=['POST'])
def set_mode():
    data = request.data.decode() #json.loads(request.data.decode())
    session['mode'] = data
    # print(colors.red+session['mode']+colors.black)
    return session['mode']

######################################################
#### import related
######################################################
@app.route('/upload_file', methods=['POST'])
def upload_file():
    try:
        f = request.files['file']
        # print(request.files)
        filename = os.path.join(session['path'],'upload',f.filename)
        f.save(filename)
        return 'ok'
    except Exception as e:
        msg='could not import file:'
        print(colors.red+msg)
        print(colors.magenta,e,colors.black)
        return "%s : %s" %(msg, e.__str__())

################
#### import frames
@app.route('/update_zenodo', methods=['POST'])
def update_zenodo():
    fetch = json.loads(request.data.decode())['fetch']
    if fetch:
        cmd = "python3 zenodo.py"
        out=check_output(cmd,shell=True).decode().strip();print(out)
    with open('static/spg/records.json','r') as f:
        records = json.load(f)
    return json.dumps(records)

@app.route('/get_dl_state', methods=['GET'])
def get_dl_state():
    log_file="%s/dl.log" %(session['path'])
    cmd=r"grep '%%'  %s" %log_file
    cmd+=r" | tail -n1 | sed -rE 's/([0-9]*%)/;\1;/g' | cut -d';' -f2"
    # print(cmd)
    dl_state=check_output(cmd,shell=True).decode().strip()
    msg='Download state : \n%s\n' %dl_state
    # print(dl_state)
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

@app.route('/check_dl_format', methods=['POST'])
def check_dl_format():
    link=request.data.decode()
    fmt=get_compressed_fmt(link)              #;print(fmt)
    if fmt not in compress_fmts:
        msg='Compressed file should be of the following formats :\n %s' %(','.join(compress_fmts))
    else:
        msg='ready to download'
    return json.dumps({'msg':msg})

@app.route('/check_dl_frames', methods=['POST'])
def check_dl_frames():
    link     = request.data.decode()          #;print(link)
    filepath = data_path(link)                #;print(filepath)
    dl       = os.path.exists(filepath)       #;print(dl)
    folders  = []
    if dl:
        cmd=r'cd {path};for dir in `find {folder} -type d`;do for fmt in {formats};do find $dir -maxdepth 1 -type f -name "*.$fmt" -not -name ".*" | head -n1;done;done'.format(
            path    = 'static/database',
            folder  = os.path.basename(filepath),
            formats = ' '.join(readers.fmts),
        )
        # print(cmd)
        files   = check_output(cmd,shell=True).decode().strip()
        folders = [os.path.dirname(f) for f in files.split('\n')]
        # print(files,folders)
    return json.dumps({'dl':dl,'folders':folders})

@app.route('/load_frames', methods=['POST'])
def load_frames():
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

################
#### import dats
@app.route('/check_dat', methods=['POST'])
def check_dat():
    filename = request.data.decode() #;print(data)
    new_filename = filename.strip('()[]').replace(' ','_')#;print(new_filename)
    data_folder  = tmp_dat_folder(session)
    unzip_cmd=''
    if filename.split('.')[-1] == 'zip':
        unzip_cmd='unzip %s >/dev/null;rm %s;' %((new_filename,)*2)

    cmd="\
if [ -d  {data_folder} ];then rm -rf {data_folder};fi;\
mkdir {data_folder};\
mv '{filepath}' {data_folder}/{new_filename};\
cd {data_folder};{unzip_cmd}\
".format(
        data_folder  = data_folder,
        unzip_cmd    = unzip_cmd,
        filepath     = os.path.join(session['path'],'upload',filename),
        new_filename = new_filename,
    )#;print(colors.magenta,cmd,colors.black)

    out=check_output(cmd,shell=True).decode().strip()#;print(out)
    dat_info=check_proc_data(data_folder)
    # print(dat_info)
    return json.dumps(dat_info)


@app.route('/import_dat', methods=['POST'])
def import_dat():
    # dat_type = request.data.decode()  #;print(folder)
    tmp_folder  = tmp_dat_folder(session)
    dat_info    = check_proc_data(tmp_folder)
    cmd = 'if [ -d {dat_path} ];then rm -rf {dat_path};fi;mv {tmp_path} {dat_path}'.format(
        tmp_path = tmp_folder,
        dat_path = os.path.join(mol_path(session['mol']),dat_info['dat_type'])
    )#;print(cmd)
    out=check_output(cmd,shell=True).decode().strip()#;print(out)
    return out

@app.route('/load_dat_type', methods=['POST'])
def load_data_type():
    dat_type = request.data.decode()
    select_dat_type(session['mol'],dat_type)

    dat_type  = load_dat_type(session['mol'])
    dat_types = get_dat_types(session['mol'])
    session['dat']['pets']      = any(dat_types)
    session['dat']['dat_type']  = dat_type
    session['dat']['dat_types'] = dat_types
    return json.dumps(session['dat'])

################
#### import cif
@app.route('/import_cif', methods=['POST'])
def import_cif():
    filename = request.data.decode() #;print(data)
    _import_cif(filename)
    crys_dat = init_structure()
    return json.dumps(crys_dat)

def _import_cif(filename):
    new_filename = filename.strip('()[]').replace(' ','_')#;print(new_filename)

    cmd="rm -f {mol_path}/*.cif; mv '{filepath}' {mol_path}/{new_filename};rm -f {path}*.cif;rm -f {path}/upload/*.cif".format(
        filepath     = os.path.join(session['path'],'upload',filename),
        mol_path     = mol_path(session['mol']),
        new_filename = new_filename,
        path         = session['path'],
    )#;print(colors.magenta,cmd,colors.black)

    out=check_output(cmd,shell=True).decode().strip()#;print(out)



######################################################
#### Structure related
######################################################
@app.route('/delete_structure', methods=['POST'])
def delete_structure():
    data = json.loads(request.data.decode())#;print(data)
    mol  =  data['mol']
    cmd='rm -rf %s' %mol_path(mol)
    out=check_output(cmd,shell=True).decode().strip()#;print(out)
    return json.dumps({'msg':out,'structures':get_structures()})

@app.route('/new_structure', methods=['POST'])
def new_structure():
    data = json.loads(request.data.decode())#;print(data)
    mol  =  data['name']
    msg  = ''

    if not mol=='' : #or mol=="new":
        new_mol_path = mol_path(mol)
        if not os.path.exists(new_mol_path):
            cmd='mkdir %s' %new_mol_path
            out=check_output(cmd,shell=True).decode().strip()#;print(out)
            # if a structure is provided
            if data['is_struct']:
                msg=import_structure_file(data)
        else:
            msg='folder %s already exists' %mol
    else:
        msg='Choose a proper name for the structure'
    # structures = get_structures()
    return json.dumps({'msg':msg,'structures':get_structures()})

@app.route('/get_structure_info', methods=['POST'])
def get_structure_info():
    data = json.loads(request.data.decode())#;print(data)
    mol  = data['mol']
    cif_file='?'
    cif_files = glob.glob(os.path.join(mol_path(mol),'*.cif'))
    if len(cif_files):
        cif_file = os.path.basename(cif_files[0])
    frames_folder   = get_frames_folder(mol,'exp',full=True)
    dat_type        = get_dat_type(mol)
    # print(mol,cif_file,dat_type,frames_folder)
    return json.dumps({
        'name': mol,
        'cif' : cif_file,
        'dat' : dat_type,
        'exp' : frames_folder,
    })


@app.route('/set_structure', methods=['POST'])
def set_structure():
    data = json.loads(request.data.decode())
    session['mol'] = data['mol']
    return 'ok'

def import_structure_file(data):
    msg = 'cif file issue'
    val = data['struct_type']
    cif_file=os.path.join(path,data[val])

    try:
        if val=='builtin' :
            crys = crystals.Crystal.from_database(data['builtin'])
            cif_file+='.cif'
            ut.crys2felix(crys,opt='w',out=cif_file)
            cif_file=data[val]
        elif val=='pdb' :
            crys = crystals.Crystal.from_pdb(data['pdb'],download_dir='.')
            cmd = 'mv pdb%s.ent %s.pdb' %(data['pdb'],data['pdb'])
            check_output(cmd,shell=True).decode().strip()
        elif val=='cif':
            _import_cif(data['cif_file'])

    except Exception as e:
        raise Exception(e)
        msg=e.__str__()
    print(msg)
    return msg

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

    ####sanity checks
    if not (session['dat']['exp'] or session['dat']['exp']) and session['mode']=='frames':
        session['mode']='bloch'

    if session['mode']=='felix' and not session['dat']['felix']:
        session['mode'] = 'bloch'
    if session['dat']['exp'] :
        if session['frame']>session['nb_frames']:
            session['frame']=1

    cmd='find static/database/ -maxdepth 1 -mindepth 1 -type  d | xargs -n1 basename'
    local_frames=check_output(cmd,shell=True).decode().strip().split('\n')
    ####### package info to frontend
    info=['mol','dat','frame','crys','mode','zmax','nb_frames',
        'offset','cmap','cmaps','heatmaps','nb_colors',
        'new','b0_path',]
    session_data = {k:session[k] for k in info}
    folder={}
    if session['dat']['exp']:
        folder['exp']=session['exp']['folder']
    if session['dat']['sim']:
        folder['sim']=session['sim']['folder']
    session_data['folder']      = folder
    session_data['builtins']    = list(builtins)
    session_data['structures']  = get_structures()
    session_data['local_frames']  = local_frames

    session['init'] = True
    # print(colors.magenta+'init done : ',session['init'],colors.black)
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

def init_structure():
    struct_file = get_structure_file()
    crys_dat=dict(zip(
    ['file','a','b','c','alpha','beta','gamma','a1', 'a2', 'a3','chemical_formula',
        'nb_atoms','lattice_system'],
    ['?']*13))
    crys_dat['spg_ref']=False
    if struct_file:
        try:
            b0=bloch.Bloch(struct_file,path=session['path'],init=False,name='b',solve=False,Nmax=1)
            print('saving bloch object')
            b0.save()
            # b0=ut.load_pkl(session['b0_path'])
        except:
            return crys_dat

        crys,cif_file = b0.crys,b0.cif_file
        crys_dat = {'file':os.path.basename(cif_file),'cif_file':cif_file}
        crys_dat.update({k:b_str(crys.__dict__[k],2) for k in ['a1', 'a2', 'a3']})
        crys_dat.update(dict(zip(['a','b','c','alpha','beta','gamma'],
            b_str(crys.lattice_parameters,2).split(',') )))
        formula = re.sub("([0-9]+)", r"_{\1}", crys.chemical_formula).replace(' ','')
        crys_dat['chemical_formula'] = formula                  #;print(formula)
        crys_dat['lattice_system']   = crys.lattice_system.name
        crys_dat['nb_atoms'] = len(crys.atoms)
        crys_dat['spg_ref']  = False
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

    # print(crys_dat)
    # print(formula)
    return crys_dat

def init_mol():
    # print(colors.red+'init_mol'+colors.black)
    mol = session['mol']
    sim = init_frames(mol,'sim')
    exp = init_frames(mol,'exp')
    if  mol not in pets_data.keys():
        dat_type = update_exp_data(mol)
    dat_type = get_dat_type(mol)
    dat = {
        'exp'       : type(exp)==dict,
        'sim'       : type(sim)==dict,
        'pets'      : type(dat_type)==str,
        'dat_type'  : dat_type,
        'dat_types' : get_dat_types(mol),
        'felix'     : os.path.exists(os.path.join(mol_path(mol),'felix')),
        'rock'      : False,
        'omega'     : 0,
        }

    upload_path=os.path.join(session['path'],'upload')
    if not os.path.exists(upload_path):
        check_output("mkdir %s" %upload_path,shell=True).decode().strip()
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

    crys_dat=init_structure()


    #related to /set_viewer
    if session.get('bloch_modes'):
        # print('mol init :',session['bloch_modes'])
        if session['bloch_modes']['u0']=='auto' and not dat['pets']:
            session['bloch_modes']['u0'] = 'edit'
    if not session.get('frame') :session['frame']  = 1
    if not session.get('offset'):session['offset'] = 0

    now = time.time()
    # session['cif_file'] = struct_file
    session['dat']        = dat
    session['crys']       = crys_dat
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
        frames_dict['folder'] = get_frames_folder(mol,frame_type)
    return frames_dict


def clear_session():
    print('warning:tmp directory %s not used since %d days. Removing content ...' %(session.get('path'),days))
    print(check_output('rm -rf %s/*' %session.get('path'),shell=True).decode())
    # init_args()
    print(colors.red+'init0'+colors.black)
