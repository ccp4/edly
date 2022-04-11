from flask import Flask,Blueprint,request,jsonify,session,render_template
from subprocess import check_output,Popen,PIPE
import json,tifffile,os,sys,glob,time,datetime #,base64,hashlib
import numpy as np,pandas as pd
from blochwave import bloch
from blochwave import bloch_pp as bl #;imp.reload(bl)
from EDutils import utilities as ut
from EDutils import pets as pt              #;imp.reload(pt)
from utils import displayStandards as dsp
from utils import glob_colors as colors
import plotly.express as px
import plotly.graph_objects as go
from in_out import*
bw_app = Blueprint('bw_app', __name__)

fig_wh=725
pets_data={}

@bw_app.route('/')
def image_viewer():
    return render_template('bloch.html')



########################
#### frame
########################
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
    session['modes']['analysis']=False
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


########################
#### Bloch
########################
@bw_app.route('/bloch_rotation', methods=['POST'])
def bloch_rotation():
    data=json.loads(request.data.decode())
    theta,phi = data['theta_phi']
    theta %=180
    phi   %=360
    session['bloch']['u'] = list(ut.u_from_theta_phi(theta,phi))
    session['bloch']['solve'] = False
    session['modes']['rotation'] = True
    session['modes']['manual']   = True
    return update_bloch()

@bw_app.route('/solve_bloch', methods=['POST'])
def solve_bloch():
    data=json.loads(request.data.decode())
    frame = data['frame']
    b_args = data['bloch']
    ## handle
    thicks = update_thicks(data['bloch']['thicks'])
    u = pets_data[session['mol']].uvw0[frame-1]
    if data['manual_mode']:
        # print(data['bloch']['u'])
        u = b_arr(data['bloch']['u'],u)

    b_args.update({'u':list(u),'thicks':list(thicks),'solve':True})
    session['modes']['manual'] = data['manual_mode']
    session['bloch'] = b_args
    # session['last_req'] = 'solve_bloch:%s' %(time.time())
    # print({k:type(v) for k,v in session['bloch'].items()})
    return update_bloch()


def update_bloch():
    b_args = session['bloch']#.copy()
    # print(b_args['u'])
    # b_args['thicks']=None
    b0 = bloch.Bloch(session['cif_file'],
        path=session['path'],name='b',**b_args)
    b0.save()

    fig_data = bloch_fig()

    session['modes']['analysis'] = True
    session['theta_phi'] = list(ut.theta_phi_from_u(b_args['u']))
    bloch_args=b_args.copy()
    bloch_args.update({'u':b_str(b_args['u'],4),'thicks':b_str(b_args['thicks'],0)})
    info = json.dumps({'fig':fig_data,'nbeams':b0.nbeams,
        'bloch':bloch_args,'theta_phi':b_str(session['theta_phi'],4)})
    return info


def bloch_fig(b0_path=''):
    if not b0_path:
        b0_path=get_pkl(session['id'])
    b0 = ut.load_pkl(b0_path)
    b0.df_G['hkl'] = b0.df_G.index
    b0.df_G['I']   *=1000
    # print(b0.thick,b0.df_G['I'].max())
    b0.df_G['Vga'] *=1000
    b0.df_G['Swa'] *=400

    ## pets
    pets = pets_data[session['mol']]
    df_pets = pets.rpl.loc[pets.rpl.eval('(F==%d) &(I>2)' %session['frame'] )]
    rpx,rpy,Ipets=df_pets[['rpx','rpy','I']].values.T

    ## plot
    toplot=b0.df_G[['px','py','I','Vga','Swa']]
    toplot=toplot.melt(value_vars=['I','Vga','Swa'],id_vars=['px','py'])
    # frame_str=str(session['frame']).zfill(session['exp']['pad'])
    # tiff_file=get_path(session['mol'],'exp',frame_str)
    # im = tifffile.imread(tiff_file)

    fig=px.scatter(toplot,x='px',y='py',
        color="variable",size='value')
    # fig.add_trace(go.scatter(x=rpx,y=rpy,size=Ipets))
    fig.update_layout(
        title="Diffraction pattern thick=%d A " %b0.thick,
        hovermode='closest',
        # margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor="LightSteelBlue",
        width=fig_wh, height=fig_wh,
    )

    # fig.update_traces(marker_size=10)
    return fig.to_json()

@bw_app.route('/show_u', methods=['POST'])
def show_u():
    data = json.loads(request.data.decode())
    if session['modes']['u']=='rock':
        r_args = get_rock(data)
        uvw = ut.get_uvw_rock(**r_args)
    else:
        uvw = np.array(b_arr(data['u'],session['bloch']['u']))[None,:]

    ui = np.arange(uvw.shape[0])[:,None]
    uvw = np.vstack([np.hstack([uvw,ui]),np.hstack([0*uvw,ui])])
    df = pd.DataFrame(uvw,columns=['u0','u1','u2','ui']) #; print(df)
    df['ui'] = np.array(df['ui'],dtype=int)
    # df = px.data.gapminder().query("continent=='Europe'")
    fig = px.line_3d(df, x="u0", y="u1", z="u2", color='ui')

    fig.update_layout(
        title="3d view of orientation vector ",
        hovermode='closest',
        # margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor="LightSteelBlue",
        width=fig_wh, height=fig_wh,
    )
    return fig.to_json()

##############################
#### Rocking curve stuffs
##############################
@bw_app.route('/rock_state', methods=['GET'])
def rock_state():
    if not session['rock_state'] == 'done':
        n_simus=len(glob.glob(os.path.join(session['path'],'u_*.pkl')))
        npts=session['rock']['npts']
        if not n_simus==npts:
            session['rock_state'] = '%d/%d' %(n_simus,npts)
        else:
            if not os.path.exists(rock_path(session['id'])):
                session['rock_state'] = 'postprocess'
            else:
                session['rock_state'] = 'done'
    print(session['rock_state'])
    return json.dumps(session['rock_state'])

@bw_app.route('/set_rock_frame', methods=['POST'])
def set_rock_frame():
    data = json.loads(request.data.decode())
    frame = data['frame']
    uvw = pets_data[session['mol']].uvw0
    u0 = uvw[max(0,frame-2)]
    u1 = uvw[frame-1]
    u2 = uvw[min(frame,frame-1)]
    e0 = (u0 + u1)/2
    e1 = (u1 + u2)/2
    e0/=np.linalg.norm(e0)
    e1/=np.linalg.norm(e1)

    session['rock'].update({'e0':e0.tolist(),'e1':e1.tolist()})
    session['frame'] = frame
    return json.dumps({'rock':get_session_data('rock')})

@bw_app.route('/set_rock', methods=['POST'])
def set_rock():
    data=json.loads(request.data.decode())
    r_args = get_rock(data)

    cmd = 'rm %s/u_*.pkl %s' %(session['path'],rock_path(session['id']))
    p=Popen(cmd,shell=True,stderr=PIPE,stdout=PIPE)
    print(p.communicate())

    session['rock_state'] = 'init'
    session['rock'] = r_args
    session['bloch'].update({k:data['bloch'][k] for k in ['keV','Nmax','Smax','thick']})
    data = {s : get_session_data(s) for s in ['rock']}
    return json.dumps(data)

def get_rock(data):
    r_args = data['rock']
    r_args.update({
        'e0' : b_arr(data['rock']['e0'],session['rock']['e0']),
        'e1' : b_arr(data['rock']['e1'],session['rock']['e1']),
    })
    return r_args

@bw_app.route('/solve_rock', methods=['POST'])
def solve_rock():
    Sargs = {k:session['bloch'][k] for k in ['keV','Nmax','Smax','thick']}
    Sargs['cif_file'] = session['cif_file']

    uvw  = ut.get_uvw_rock(**session['rock'])
    rock = bl.Bloch_cont(path=session['path'],tag='',uvw=uvw,Sargs=Sargs)
    session['rock_state'] = 'done'
    nbeams = np.array([rock.load(i).nbeams for i  in range(rock.n_simus)] )
    nbs = '%d-%d' %(nbeams.min(),nbeams.max())
    return json.dumps({'nbeams':nbs})

@bw_app.route('/overlay_rock', methods=['POST'])
def overlay_rock():
    sim = glob.glob(os.path.join(session['path'],'u_*.pkl'))[0]
    return bloch_fig(b0_path=sim)

@bw_app.route('/get_rock_sim', methods=['POST'])
def get_rock_sim():
    data = json.loads(request.data.decode())
    rock_sim = int(data['sim'])
    print(rock_sim)
    sims = glob.glob(os.path.join(session['path'],'u_*.pkl'))
    i    = max(min(rock_sim,len(sims)),1)-1
    sim  = sims[i];print(i,sim)
    fig = bloch_fig(b0_path=sim)
    return json.dumps({'fig':fig, 'sim':i+1})

@bw_app.route('/show_rock', methods=['POST'])
def show_rock():
    data = json.loads(request.data.decode())
    refl = data['refl']
    rock = ut.load_pkl(file=rock_path(session['id']))

    # z,I  = rock.get_rocking(refl=refl)
    refl0 = str(tuple(refl[0]))
    Sw = rock.beams.loc[refl0].Sw
    I  = [rock.load(i).df_G.loc[refl0,'I'] for i in range(rock.n_simus)]
    # print(Sw,I)

    ### the figure
    fig = px.scatter(x=Sw,y=I)
    fig.update_layout(
        title="Rocking curve",
        hovermode='closest',
        paper_bgcolor="LightSteelBlue",
        width=fig_wh, height=fig_wh,
    )
    return fig.to_json()

########################
#### Thickness stuffs
########################
@bw_app.route('/update_thickness', methods=['POST'])
def update_thickness():
    thick = json.loads(request.data.decode())['thick']
    b0 = ut.load_pkl(get_pkl(session['id']))
    b0.set_thickness(thick=thick)
    b0.save(get_pkl(session['id']))
    session['bloch']['thick'] = thick
    return bloch_fig()

def update_thicks(thicks):
    thicks = tuple(np.array(b_arr(thicks,(0,100,100)),dtype=int).tolist())
    session['bloch']['thicks'] = thicks
    return thicks

@bw_app.route('/beam_vs_thick', methods=['POST'])
def beam_vs_thick():
    data = json.loads(request.data.decode())
    refl = data['refl']
    thicks = update_thicks(data['thicks'])

    b0  = ut.load_pkl(get_pkl(session['id']))
    idx = b0.get_beam(refl=refl)
    b0._set_beams_vs_thickness(thicks=thicks)
    Iz  = b0.get_beams_vs_thickness(idx=idx)
    b0.save(get_pkl(session['id']))

    ### the figure
    fig = px.scatter(x=b0.z,y=Iz[0,:])#,color="red")
    fig.update_layout(
        title="thickness dependent intensities",
        hovermode='closest',
        # margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor="LightSteelBlue",
        width=fig_wh, height=fig_wh,
    )
    return fig.to_json()


########################
#### structure related
########################
@bw_app.route('/set_mode', methods=['POST'])
def set_mode():
    data = json.loads(request.data.decode())
    # print(data)
    key  = data['key']
    session['modes'][key] = data['val']
    session['mol']  = session['mol']
    return json.dumps({key:session['modes'][key]})

@bw_app.route('/set_structure', methods=['POST'])
def set_structure():
    data=json.loads(request.data.decode())
    cif_file=os.path.join(mol_path(session['mol']),'pets',data['cif'])
    session['cif'] = data['cif']
    session['cif_file'] = cif_file
    return session['cif_file']

############################################################################
#### Init
############################################################################
@bw_app.route('/init', methods=['GET'])
def init():
    now = time.time()
    if session.get('id') and os.path.exists(session.get('path')):
        if (now-session['last_time'])>24*3600:
            print('warning:session create at %s has expired ' %session['last_time'])
            print(check_output('rm -rf %s/*' %session.get('path'),shell=True).decode())
    else:
        id = create_id()
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
        bloch_args={'keV':200,'u':[0,0,1],'Nmax':4,'Smax':0.02,
            'thick':250,'thicks':[0,300,100],'opts':'vts','solve':1}

        modes = {
            'molecule'  :False,
            'analysis'  :True,
            'manual'    :False,
            'u'         :'edit',
            'single'    :False,
        }
        rock_args = {'e0':[0,3,1],'e1':[2,1],'deg':0.5,'npts':3,'show':0}

        session['id']   = id
        session['path'] = session_path
        session['mol']  = mol
        session['cif']  = 'alpha_glycine.cif'
        # session['cif'] = '1ejg.pdb'
        session['cif_file'] = os.path.join(mol_path(mol),'pets',session['cif'])
        session['frame'] = 1
        session['sim']   = sim
        session['exp']   = exp
        session['modes'] = modes
        session['zm_counter'] = 0 #dummy variable
        session['theta_phi']  = [0,0]
        session['bloch']      = bloch_args
        session['rock']       = rock_args
        session['last_time']  = now
        session['time'] = now
        # print(session['cif'],session.get('exp'+'tmp'))

    if not session['mol'] in pets_data.keys():
        pets_data[session['mol']]=pt.Pets(pets_path(session['mol']),gen=False,dyn=1)


    print('send init info')
    info=['mol','frame','cif','cif_file','modes']
    session_data = {k:session[k] for k in info}
    session_data['max_frame']=session['exp']['max_frame']
    for k in ['zmax']:
        session_data[k] = dict(zip(['sim','exp'],[session['sim'][k],session['exp'][k]]))
    session_data['theta_phi']=b_str(session['theta_phi'],2)
    session_data['bloch']=get_session_data('bloch')
    session_data['rock']=get_session_data('rock')
    return json.dumps(session_data)

def get_session_data(key):
    if key=='bloch':
        data=session['bloch'].copy()
        data.update({'u':b_str(session['bloch']['u'],4),
            'thicks':b_str(session['bloch']['thicks'],0)})
    elif key == 'rock':
        data=session['rock'].copy()
        data.update({
            'e0':b_str(session['rock']['e0'],4),
            'e1':b_str(session['rock']['e1'],4),
        })
    return data
