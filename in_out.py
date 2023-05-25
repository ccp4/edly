from string import ascii_letters,digits
import os,glob,crystals,numpy as np
from subprocess import check_output
from crystals import Crystal as Crys
from utils import glob_colors as colors
from EDutils import felix as fe        #;imp.reload(fe)
from EDutils import pets               #;imp.reload(pets)
from EDutils import dials_utils as dials#;imp.reload(dials)
from EDutils import xds                 #;imp.reload(xds)

chars = ascii_letters+digits
mol_path=lambda mol:'static/data/%s' %mol
# get_path=lambda mol,key,frame_str:os.path.join(mol_path(mol),key,'%s.tiff' %frame_str)
get_path   = lambda mol,key,frame_str:os.path.join(mol_path(mol),key,frame_str)
pets_path  = lambda mol:os.path.join(mol_path(mol),'pets','%s.pts' %mol)
dials_path = lambda mol:os.path.join(mol_path(mol),'dials')
xds_path   = lambda mol:os.path.join(mol_path(mol),'xds','XDS_ASCII.HKL')
get_pkl    = lambda id:'static/data/tmp/%s/b.pkl' %id
rock_path  = lambda id:'static/data/tmp/%s/rock_.pkl' %id
felix_path = lambda mol:os.path.join(mol_path(mol),'felix')
felix_pkl  = lambda session:os.path.join(felix_path(session['mol']),'felix.pkl')

pets_data={}

def update_exp_data(mol):
    dat_type=None
    if os.path.exists(dials_path(mol)):
        dat_type='dials'
    elif os.path.exists(pets_path(mol)):
        dat_type='pets'
    elif os.path.exists(xds_path(mol)):
        dat_type='xds'

    if not mol in pets_data.keys():
        if os.path.exists(dials_path(mol)):
            pets_data[mol]=dials.Dials(dials_path(mol))
        elif os.path.exists(pets_path(mol)):
            pets_data[mol]=pets.Pets(pets_path(mol),gen=False,dyn=0)
        elif os.path.exists(xds_path(mol)):
            pets_data[mol]=xds.XDS(xds_path(mol))
    print(colors.red+'processed data type for structure %s : %s' %(mol,dat_type)+colors.black)
    return dat_type

def load_pets(session):
    pts_file = pets_path(session['mol'])
    if os.path.exists(pts_file):
        return pets.Pets(pts_file)

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

structures = [os.path.basename(s) for s in glob.glob("static/data/*") if not s=="static/data/tmp"]
builtins = crystals.Crystal.builtins
gifs = {os.path.basename(s)[:-4]:s for s in glob.glob("static/gifs/*")}
fig_wh=725

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
