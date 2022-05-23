from string import ascii_letters,digits
import os,glob
import numpy as np
from crystals import Crystal as Crys
import crystals

chars = ascii_letters+digits
mol_path=lambda mol:'static/data/%s' %mol
get_path=lambda mol,key,frame_str:os.path.join(mol_path(mol),key,'%s.tiff' %frame_str)
png_path=lambda path,frame_str:os.path.join(path,'%s.png' %frame_str)
pets_path=lambda mol:glob.glob(os.path.join(mol_path(mol),'pets','*.pts'))[0]
get_pkl  =lambda id:'static/data/tmp/%s/b.pkl' %id
rock_path=lambda id:'static/data/tmp/%s/rock_.pkl' %id


structures = [os.path.basename(s) for s in glob.glob("static/data/*") if not s=="static/data/tmp"]
builtins = crystals.Crystal.builtins
gifs = {os.path.basename(s)[:-4]:s for s in glob.glob("static/gifs/*")}

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
