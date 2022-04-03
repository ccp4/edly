from flask import Flask,Blueprint,request,jsonify,session,render_template
from subprocess import check_output,Popen,PIPE
import json,tifffile,os,sys,glob,time,datetime #,base64,hashlib
import numpy as np
from blochwave import bloch
from EDutils import utilities as ut
from utils import displayStandards as dsp
from EDutils import pets as pt              #;imp.reload(pt)
from utils import glob_colors as colors
import plotly.express as px
import plotly.graph_objects as go
from string import ascii_letters,digits
bw_app = Blueprint('bw_app', __name__)

chars = ascii_letters+digits
mol_path=lambda mol:'static/data/%s' %mol
get_path=lambda mol,key,frame_str:os.path.join(mol_path(mol),key,'%s.tiff' %frame_str)
png_path=lambda path,frame_str:os.path.join(path,'%s.png' %frame_str)
def b_str(x,i):
    if i:
        n=10**i
        return str(tuple(np.round(np.array(x)*n)/n))[1:-1]
    else:
        return str(tuple(x))[1:-1]
    return
def b_arr(x,x0):
    try :
        y = np.array(x.split(","), dtype=float)
        if not y.size==3:y=x0
        return y
    except:
        return x0
fig_wh=780

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
    data=json.loads(request.data.decode())
    frame = data['frame']
    pets_path = glob.glob(os.path.join(mol_path(session['mol']),'pets','*.pts'))
    pets = pt.Pets(pets_path[0],gen=False,dyn=1)
    df_pets=pets.rpl.loc[pets.rpl.eval('(F==%d) &(I>2)' %frame )]
    rpx,rpy,Ipets=df_pets[['rpx','rpy','I']].values.T
    # print(data)
    b_args = data['bloch']
    thicks  = np.array(b_arr(data['bloch']['thicks'],(0,100,100)),dtype=int)
    u       = pets.uvw0[frame-1]
    # u = ut.u_from_theta_phi(theta,phi)
    keV     = 200
    if data['manual_mode']:
        u = eval(data['bloch']['u'],pets.uvw0[frame-1])
    b_args.update({'keV':keV,'u':u,'thicks':thicks})

    # print(b_args)
    b0 = bloch.Bloch(session['cif_file'],path='dat/',**b_args)
    # b0.df_G[['I','Vga','Swa']]*=200
    b0.df_G['hkl'] = b0.df_G.index
    b0.df_G['I']   *=1000
    b0.df_G['Vga'] *=1000
    b0.df_G['Swa'] *=400

    ## plot
    toplot=b0.df_G[['px','py','I','Vga','Swa']]
    # fig=px.scatter(b0.df_G,x='px',y='py',size='I',)
    toplot=toplot.melt(value_vars=['I','Vga','Swa'],id_vars=['px','py'])
    frame_str=str(session['frame']).zfill(session['exp']['pad'])
    tiff_file=get_path(session['mol'],'exp',frame_str)
    # im = tifffile.imread(tiff_file)

    # fig = go.Figure()
    # fig=px.imshow(im)
    fig=px.scatter(toplot,x='px',y='py',
        color="variable",size='value')
    # fig.add_trace(go.scatter(toplot,x='px',y='py',
    #     color="species", symbol="species",size='value'))
    # fig.add_trace(go.scatter(x=rpx,y=rpy,size=Ipets))
    fig.update_layout(
        title="Diffraction pattern thick=%d A " %b0.thick,
        hovermode='closest',
        # margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor="LightSteelBlue",
        width=fig_wh, height=fig_wh,
    )

    # fig.update_traces(marker_size=10)


    fig_data = fig.to_json()


    b_args.update({'u':b_str(u,4),'thicks':b_str(thicks,0)})
    session['bloch'] = b_args
    session['manual_mode']   = data['manual_mode']
    session['analysis_mode'] = True
    # print(session['bloch'])
    return json.dumps({'fig':fig_data,'bloch':session['bloch'],'nbeams':b0.nbeams})

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
        bloch_args={'keV':200,'u':b_str([0,0,1],4),'Nmax':6,'Smax':0.05,
            'thick':10,'thicks':b_str([0,10,100],0),'opts':'svt'}

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
        session['manual_mode']   = False
        session['show_molecule'] = False
        session['zm_counter'] = 0 #dummy variable
        session['bloch']      = bloch_args
        session['last_time']  = now
        # print(session['cif'],session.get('exp'+'tmp'))

    print('send init info')
    info=['mol','frame','cif','cif_file','show_molecule',
        'analysis_mode','bloch','manual_mode']
    session_data = {k:session[k] for k in info}
    session_data['max_frame']=session['exp']['max_frame']
    for k in ['zmax']:
        session_data[k] = dict(zip(['sim','exp'],[session['sim'][k],session['exp'][k]]))
    return json.dumps(session_data)
