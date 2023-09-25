from string import ascii_letters,digits
import os,glob,crystals,numpy as np
from subprocess import check_output
from crystals import Crystal as Crys
from utils import glob_colors as colors
from EDutils import felix as fe        #;imp.reload(fe)
from EDutils import pets               #;imp.reload(pets)
from EDutils import dials_utils as dials#;imp.reload(dials)
from EDutils import xds                 #;imp.reload(xds)
from EDutils import readers

chars = ascii_letters+digits
mol_path=lambda mol:'static/data/%s' %mol
get_path   = lambda mol,key,frame_str:os.path.join(mol_path(mol),key,frame_str)
#data processing paths
pets_path  = lambda mol:os.path.join(mol_path(mol),'pets')#,'%s.pts' %mol)
dials_path = lambda mol:os.path.join(mol_path(mol),'dials')
xds_path   = lambda mol:os.path.join(mol_path(mol),'xds','XDS_ASCII.HKL')
dat_path   = lambda mol:os.path.join(mol_path(mol),'dat')
tmp_dat_folder = lambda session:os.path.join(session['path'],'tmp_dat')
proc_dat_files  = {
    'xds'  : ['XDS_ASCII.HKL'],
    'pets' : ['*.pts','*.rpl','*.xyz','*.cor','*.hkl','*.cenloc','*.cif_pets','*_dyn.cif_pets','*.cif'],
    'dials': ['*.expt', '*.refl','reflections.txt'],
    }


def get_frames_fmt(path):
    '''return the type of frames in the folder if any '''
    fmts = readers.fmts
    files = glob.glob(os.path.join(path,'*.*'))
    if not len(files):return ''
    #detect format
    fmt,i = '',0
    while fmt not in fmts and i<len(files):
        fmt = files[i].split('.')[-1]
        i+=1
    if fmt not in fmts:fmt =""
    return fmt

def get_local_frames_folder():
    local_frames_link='static/database'
    if not os.path.exists(local_frames_link):
        check_output("mkdir database;cd static; ln -s ../database .",shell=True).decode().strip()
    local_frames_path=check_output("realpath $(readlink %s)" %local_frames_link,shell=True).decode().strip()
    return local_frames_path
local_frames_path = get_local_frames_folder()

def check_proc_data(path):
    missing_files='?'
    dtype='unknown'
    for dat_type,dat_files in proc_dat_files.items():
        files = np.array([len(glob.glob(os.path.join(path,f)))>=1
            for f in dat_files])
        if ~all(files) and any(files):
            dtype=dat_type
            missing_files=', '.join(np.array(dat_files)[~files])
        if all(files):
            dtype=dat_type;
            missing_files=''
            break
    return {'dat_type':dtype,'missing_files':missing_files}

### simulations paths
get_pkl    = lambda id:'static/data/tmp/%s/b.pkl' %id
rock_path  = lambda id:'static/data/tmp/%s/rock_.pkl' %id
felix_path = lambda mol:os.path.join(mol_path(mol),'felix')
felix_pkl  = lambda session:os.path.join(felix_path(session['mol']),'felix.pkl')
sim_path   = lambda mol:os.path.join(mol_path(mol),'rocks')

def data_path(link):
    filename=os.path.basename(link.replace('?download=1',''))
    fmt=get_compressed_fmt(filename)                         #;print('fmt:',fmt)
    #not good but should work
    if fmt:
        record=''
        if 'zenodo.org' in link :
            # print(link.split('record/'))
            record=link.split('record/')[1].split('/files')[0]
        elif 'http' in link:
            record=link.split('/')[2].replace('.','_').replace(':','_')
        folder='%s_%s' %(record,filename)
    else:
        folder=filename

    folder=folder.replace('.%s' %fmt,'')
    return 'static/database/%s' %folder

uncompress_fmts={
    'zip'       :'unzip',
    # 'h5'        :'',
    'bz2'       :'bunzip2',
    'rar'       :'unrar',
    'tar'       :'tar -xvf',
    'ser.bz2'   :'bunzip2',
    'tar.bz2'   :'tar -xvjf',
    'tar.gz'    :'tar -xvzf',
    'tar.xz'    :'tar -xJf',
    # 'LP'        :'',
    # 'LP.bz2'    :''
}
compress_fmts = list(uncompress_fmts.keys())
def get_compressed_fmt(link):
    filename=os.path.basename(link.replace('?download=1',''))   #;print(filename)
    fmts=[fmt for fmt in compress_fmts if fmt in filename]      #;print(fmts)
    if len(fmts)==1:
        return fmts[0]
    elif len(fmts)>1:
        return fmts[-1]
    else:
        return ''

pets_data={}
def get_frames_folder(mol,frame_type,full=False):
    '''get the actual name of the frames folder as defined in the database
    - full :
        True  : returns the whole path from the database root folder
        False : returns the basename of the folder only
    '''
    folder=""
    frame_path  = os.path.join(mol_path(mol),frame_type)
    if os.path.exists(frame_path):
        if full:
            cmd = "readlink %s" %frame_path
            folder=check_output(cmd,shell=True).decode().strip()
            # ;print('folder : ' ,folder)
            folder=folder.replace('%s' %local_frames_path,'')#.split(';')[1]
        else:
            cmd = "basename `readlink %s`" %frame_path
            folder=check_output(cmd,shell=True).decode().strip()
    return folder

def get_dat_types(mol):
    dat_types = [dat_type  for dat_type in ['dials','pets','xds']
        if os.path.exists(os.path.join(mol_path(mol),dat_type))]
    return dat_types

def load_dat_type(mol):
    dat_type = get_dat_type(mol)        #;print(dat_type)
    if dat_type=='dials':
        pets_data[mol]=dials.Dials(dials_path(mol))
    elif dat_type=='pets':
        pets_data[mol]=pets.Pets(path=pets_path(mol),gen=False,dyn=0)
    elif dat_type=='xds':
        pets_data[mol]=xds.XDS(xds_path(mol))
    # print(list(pets_data.keys()))
    print(colors.green+'processed data type for structure %s : %s' %(mol,dat_type)+colors.black)
    return dat_type

def get_dat_type(mol):
    dat_type=None
    if os.path.exists(dat_path(mol)):
        cmd = 'basename `readlink %s`' %dat_path(mol)      #;print(cmd)
        dat_type = check_output(cmd,shell=True).decode().strip()#;print(dat_type)
    return dat_type

def select_dat_type(mol,dat_type):
    cmd = 'cd {mol_path};if [ -L dat ];then rm dat;fi;ln -s {dat_type} dat'.format(
        dat_type = dat_type,
        mol_path = mol_path(mol),
    )
    out = check_output(cmd,shell=True).decode().strip();print(out)


def update_exp_data(mol):
    dat_type=''
    dat_types=get_dat_types(mol)
    if len(dat_types):
        #if data are available but no link is found,
        #create one for the first available data
        if not os.path.exists(dat_path(mol)):
            select_dat_type(mol,dat_types[0])
        dat_type=load_dat_type(mol)
    return dat_type

def load_felix(session):
    if not os.path.exists(felix_pkl(session)):
        # felix_path = os.path.dirname(felix_pkl(session['mol']))
        # print(colors.red+felix_path+colors.black)
        # print(glob.glob(felix_path+'/*_dyn.cif_pets'))
        fe.Felix(felix_path(session['mol']),session['mol'])
        # out=check_output("ln -s %s/felix.pkl %s" %(felix_path,mol_path(session['mol'])),shell=True).decode()
        # if out:print(out)
        print(colors.red+'felix created sucessfully'+colors.black)
    return fe.load_felix(felix_path(session['mol']))

def get_structures():
    structures =[os.path.basename(s)
        for s in glob.glob("static/data/*") if not s=="static/data/tmp"]
    return structures

builtins = crystals.Crystal.builtins
gifs = {os.path.basename(s)[:-4]:s for s in glob.glob("static/gifs/*")}
fig_wh=725

dummy_crys = dict(zip(
['file','a','b','c','alpha','beta','gamma','a1', 'a2', 'a3','chemical_formula',
    'nb_atoms','lattice_system'],
['?']*13))
dummy_crys['spg_ref']=False


def b_str(x,i):
    if i:
        n=10**i
        return str(tuple(np.round(np.array(x)*n)/n))[1:-1]
    else:
        return str(tuple(x))[1:-1]
    return
def b_arr(x,x0):
    try :
        y = np.array(x.split(","), dtype=float).tolist()
        if not len(y)==3:y=list(x0)
        return y
    except:
        return list(x0)

def create_id():
    id=''.join([chars[s] for s in np.random.randint(0,len(chars),10)])
    return id

def normalize(s):
    '''to use it as marker size data are positive and the mean should be around 30'''
    s+=-s.min()
    s/=s.max()
    s*=30
    # s = (s-s.min())/s.max()*30
    return s
