# import importlib as imp
from subprocess import check_output,Popen,PIPE
import json,tifffile,os,sys,glob,time,datetime,crystals #,base64,hashlib
from flask import Flask,Blueprint,request,url_for,redirect,jsonify,session,render_template
from functools import wraps
import numpy as np,pandas as pd
from blochwave import bloch
from blochwave import bloch_pp as bl        #;imp.reload(bl)
from EDutils import utilities as ut
from EDutils import pets as pt              #;imp.reload(pt)
from EDutils import felix as fe              #;imp.reload(fe)
from scattering import scattering_factors as scatf
from utils import displayStandards as dsp
from utils import glob_colors as colors
import plotly.express as px
import plotly.graph_objects as go
from in_out import*
bw_app = Blueprint('bw_app', __name__)

pets_data = {}
felix_data = {}


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


@bw_app.route('/upload_cif', methods=['POST'])
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


@bw_app.route('/new_structure', methods=['POST'])
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
                    init_session()
                    msg='ok'
            except Exception as e:
                check_output('rm -rf %s' %path,shell=True)
                raise Exception(e)
                msg=e.__str__()
        else:
            msg='%s already exists' %mol
    print(msg)
    return msg


########################
#### functions
########################
def normalize(s):
    '''to use it as marker size data are positive and the mean should be around 30'''
    s+=-s.min()
    s/=s.max()
    s*=30
    # s = (s-s.min())/s.max()*30
    return s

def bloch_fig():
    b0 = ut.load_pkl(session['b0_path'])
    toplot=b0.df_G[['px','py','I','Vga','Sw']].copy()

    omega=session['omega']
    # session['vis']
    if omega and session['dat']['pets']:
        ct,st = np.cos(np.deg2rad(omega)),np.sin(np.deg2rad(omega))
        qx_b,qy_b = toplot[['px','py']].values.T
        # print(qy_b[0])
        qx,qy = ct*qx_b-st*qy_b,st*qx_b+ct*qy_b
        toplot['px'],toplot['py'] = qx,qy

    plts = {
        'I'  :['Ix','blue' ,'circle'     ],
        'Vga':['Vx','yellow','triangle-up'],
        'Sw' :['Sx','red'  ,'diamond'    ],
    }
    toplot['Ix']=normalize( np.log10(np.maximum(abs(toplot['I'])  ,1e-5)))
    toplot['Vx']=normalize( np.log10(np.maximum(abs(toplot['Vga']),1e-5)))
    toplot['Sx']=normalize(-np.log10(np.maximum(abs(toplot['Sw']) ,1e-5)))
    toplot.index.name='miller indices'

    fig=go.Figure()
    for k,(v,c,m) in plts.items():
        customdata=np.array([toplot[k].values, toplot.index.to_numpy()]).T
        fig.add_trace(go.Scatter(
            x=toplot['px'],y=toplot['py'],marker_size=toplot[v],
            name=k,
            visible=session['vis'][k],
            hovertext=[k]*len(toplot),
            marker_symbol=m,marker_color=c,
            customdata=customdata,
            hovertemplate='<b>%{hovertext}</b><br><br>rpx=%{x:.3f}<br>rpy=%{y:.3f}<br>value=%{customdata[0]:.2e}<br>miller indices=%{customdata[1]}<extra></extra>',
            mode='markers',
        ))

    #### pets
    if session['dat']['pets']:
        pets = pets_data[session['mol']]
        df_pets=pets.rpl.loc[pets.rpl.eval('(F==%d) & (I>2)' %session['frame'])]
        pt_plot=df_pets[['qx','qy','I','hkl','F']].copy()
        pt_plot['Ix']=normalize(np.log10(np.maximum(abs(pt_plot['I']),1e-2)))

        fig.add_trace(go.Scatter(
            x=pt_plot['qx'],y=-pt_plot['qy'],marker_size=pt_plot['Ix'],
            name='I_pets',
            visible=session['vis']['I_pets'],
            hovertext=['I_pets']*len(pt_plot),
            marker_symbol='square',marker_color='purple',
            customdata=np.array([pt_plot['I'].values, pt_plot['hkl'].to_numpy()]).T,
            hovertemplate='<b>%{hovertext}</b><br><br>rpx=%{x}<br>rpy=%{y}<br>value=%{customdata[0]:.2f}<br>miller indices=%{customdata[1]}<extra></extra>',
            mode='markers',
        ))

    xm = session['max_res']
    if not xm:
        xm = b0.df_G.q.max()
    dq_ring = session['dq_ring']
    t,qs = np.linspace(0,2*np.pi,100),np.arange(dq_ring,xm,dq_ring)
    for q0 in qs:
        name='%.2f A' %(1/q0)
        fig.add_trace(go.Scatter(
            x=q0*np.cos(t),y=q0*np.sin(t),
            legendgroup="resolution rings",
            legendgrouptitle_text="res rings",
            name=name,hovertext=['q=%.3f recA' %q0]*t.size,
            hovertemplate='<b>ring</b><br>%{hovertext}<br>res='+name+'<extra></extra>',
            visible=session['vis']['rings'],
            mode='lines',marker_color='purple',
        ))
    offset=3+session['dat']['pets']
    rings=list(range(offset,offset+qs.size))
    session['rings']=rings#json.dumps(rings)

    fig.update_layout(
        title="diffraction pattern z=%d A" %b0.thick,
        paper_bgcolor='LightSteelBlue',#cdcfd1',
        # plot_bgcolor ='LightSteelBlue',#79a3f7',
        width=fig_wh, height=fig_wh,
    )
    # fig.update_traces(mode='markers')
    fig.update_xaxes(range=[-xm,xm])
    fig.update_yaxes(range=[xm,-xm])
    return fig.to_json()

########################
#### frame
########################
@bw_app.route('/get_frame', methods=['POST'])
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

@bw_app.route('/update_zmax', methods=['POST'])
def update_zmax():
    data=json.loads(request.data.decode())
    img=get_img_frame(session['frame'],data['zmax'],data['key'])
    session['zm_counter']+=1
    return img

def get_img_frame(frame,zmax,key):
    session['modes']['analysis']='frames'
    offset = ''
    if key=='sim':
        frame=min(max(1,frame-session['sim']['offset']),session['sim']['max_frame'])
        offset='(%d frames offset )' %session['sim']['offset']
    frame_str=str(frame).zfill(session[key]['pad'])
    png_file=png_path(session['path'],'%s_%s' %(key,frame_str))
    if not os.path.exists(png_file) or not zmax==session[key]['z_max'][frame-1]:
        tiff_file=get_path(session['mol'],key,frame_str)
        im = tifffile.imread(tiff_file)
        dsp.stddisp(im=[im],caxis=[0,zmax],cmap='viridis',
            figsize=(10,)*2,
            pOpt="p", axPos=[0.05,0.05,0.9,0.9],
            name=png_file,title='frame %s %s' %(frame_str,offset), opt='sc')

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


########################################################################
########################################################################
#### Bloch
########################################################################
########################################################################
@bw_app.route('/update_omega', methods=['POST'])
def update_omega():
    data=json.loads(request.data.decode())
    session['omega']=data['omega']
    return bloch_fig()

@bw_app.route('/bloch_rotation', methods=['POST'])
def bloch_rotation():
    data=json.loads(request.data.decode())
    theta,phi = data['theta_phi']
    theta %=180
    phi   %=360
    session['bloch']['u'] = list(ut.u_from_theta_phi(theta,phi))
    # session['bloch']['solve'] = False
    session['modes']['rotation'] = True
    session['modes']['manual']   = True
    return update_bloch()

@bw_app.route('/bloch_u', methods=['POST'])
def bloch_u():
    data=json.loads(request.data.decode())
    b_args = data['bloch']
    ## handle
    thicks = update_thicks(data['bloch']['thicks'])
    # u = pets_data[session['mol']].uvw[data['frame']-1]
    if data['manual_mode']:
        # print(data['bloch']['u'])
        u = b_arr(data['bloch']['u'],session['bloch']['u'])
    else:
        u = -pets_data[session['mol']].uvw0[data['frame']-1]
    # print(data['frame'],u)
    # print(pets_data[session['mol']].uvw[data['frame']-1])

    b_args.update({'u':list(u),'thicks':list(thicks)})
    session['frame'] = data['frame']
    session['modes']['manual'] = data['manual_mode']
    session['bloch'] = b_args
    # session['last_req'] = 'solve_bloch:%s' %(time.time())
    # print({k:type(v) for k,v in session['bloch'].items()})
    return update_bloch()

def update_bloch():
    b_args = session['bloch']#.copy()
    # print(b_args['u'])
    # b_args['thicks']=None
    b0 = ut.load_pkl(session['b0_path'])
    b0.update(**b_args)
    # b0.save()

    # session['modes']['analysis'] = 'bloch'
    session['b0_path'] = get_pkl(session['id'])
    session['theta_phi'] = list(ut.theta_phi_from_u(b_args['u']))
    bloch_args=b_args.copy()
    bloch_args.update({'u':b_str(b_args['u'],4),'thicks':b_str(b_args['thicks'],0)})
    if session['bloch']['felix']:
        fig_data=go.Figure().to_json()
    else:
        fig_data = bloch_fig()
    info = json.dumps({'fig':fig_data,'nbeams':b0.nbeams,'rings':session['rings'],
        'bloch':bloch_args,'theta_phi':b_str(session['theta_phi'],4)})
    return info

@bw_app.route('/solve_bloch', methods=['POST'])
def solve_bloch():
    b0 = ut.load_pkl(session['b0_path'])
    b0.solve(opts='vts',felix=session['bloch']['felix'])#opts=session['bloch']['opts'])
    # fig_data.show()
    # fig_data=fig_data.to_json()
    return bloch_fig()

@bw_app.route('/show_u', methods=['POST'])
def show_u():
    data = json.loads(request.data.decode())
    if session['modes']['manual']:
        if session['modes']['u']=='rock':
            r_args = get_rock(data)
            uvw = ut.get_uvw_cont(**r_args)
        else:
            uvw = np.array(b_arr(data['u'],session['bloch']['u']))[None,:]
    else:
        uvw = pets_data[session['mol']].uvw0

    ui = np.arange(uvw.shape[0])[:,None]
    uvw = np.vstack([np.hstack([uvw,ui]),np.hstack([0*uvw,ui])])
    df = pd.DataFrame(uvw,columns=['u0','u1','u2','ui']) #; print(df)
    df['ui'] = np.array(df['ui'],dtype=int)
    # df = px.data.gapminder().query("continent=='Europe'")
    fig = px.line_3d(df, x="u0", y="u1", z="u2", color='ui')

    xm=1;
    fig.update_layout(
        title="3d view of orientation vector ",
        hovermode='closest',
        # margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor="LightSteelBlue",
        width=fig_wh, height=fig_wh,
        scene = dict(
            xaxis = dict(range=[-xm,xm]),
            yaxis = dict(range=[-xm,xm]),
            zaxis = dict(range=[-xm,xm]),
        )
    )
    # print('3d fig completed')
    session['graph']='u3d'
    return fig.to_json()

##############################
#### Rocking curve stuffs
##############################
@bw_app.route('/rock_state', methods=['GET'])
def rock_state():
    if not session['rock_state'] == 'done':
        n_simus=len(glob.glob(os.path.join(session['path'],'u_*.pkl')))
        npts=session['rock']['nframes']
        if not n_simus==npts:
            session['rock_state'] = '%d/%d' %(n_simus,npts)
        else:
            if not os.path.exists(rock_path(session['id'])):
                session['rock_state'] = 'postprocess'
            else:
                session['rock_state'] = 'done'
    # print(session['rock_state'])
    return json.dumps(session['rock_state'])

@bw_app.route('/bloch_state', methods=['GET'])
def bloch_state():
    state='unknown'
    log = os.path.join(session['path'],'felix/felix.log')
    # print(glob.glob(session['path']+'/felix/felix.log'))
    if os.path.exists(log):
        with open(log,'r') as f:lines=f.readlines()
        nlines = len(lines)
        if nlines<11    : state='mpi init'
        elif nlines<15  : state='structure factors' #Mean inner potential
        elif nlines<18  : state='Absorption'        #Starting absorption calculation..
        elif nlines==18 : state='Solving'           #Bloch wave calculation...
        elif nlines<32  : state='postprocessing'    #Writing simulations for
        else            : state='Completed'
        if any(['Error' in l for l in lines]):state='error'

    session['bloch_state']=state
    return session['bloch_state'] #json.dumps()

@bw_app.route('/set_rock_frame', methods=['POST'])
def set_rock_frame():
    data = json.loads(request.data.decode())
    frame = data['frame']
    opt= data['opt']
    uvw = pets_data[session['mol']].uvw0
    if opt==0:
        e0 = uvw[max(0,frame-1)]
        e1 = np.array(session['rock']['u1'])
    elif opt==1:
        e0 = np.array(session['rock']['u0'])
        e1 = uvw[max(0,frame-1)]
    else:
        u0 = uvw[max(0,frame-2)]
        u1 = uvw[frame-1]
        u2 = uvw[min(frame,frame-1)]
        e0 = (u0 + u1)/2
        e1 = (u1 + u2)/2
        e0/=np.linalg.norm(e0)
        e1/=np.linalg.norm(e1)

    session['rock'].update({'u0':e0.tolist(),'u1':e1.tolist()})
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
        'u0' : b_arr(data['rock']['u0'],session['rock']['u0']),
        'u1' : b_arr(data['rock']['u1'],session['rock']['u1']),
    })
    return r_args

@bw_app.route('/solve_rock', methods=['POST'])
def solve_rock():
    Sargs = {k:session['bloch'][k] for k in ['keV','Nmax','Smax','thick']}
    Sargs['cif_file'] = session['cif_file']

    uvw  = ut.get_uvw_cont(**session['rock'])
    # print(session['rock'],uvw)
    rock = bl.Bloch_cont(path=session['path'],tag='',uvw=uvw,Sargs=Sargs)
    session['rock_state'] = 'done'
    nbeams = np.array([rock.load(i).nbeams for i  in range(rock.n_simus)] )
    nbs = '%d-%d' %(nbeams.min(),nbeams.max())
    return json.dumps({'nbeams':nbs})

@bw_app.route('/overlay_rock', methods=['POST'])
def overlay_rock():
    sim = glob.glob(os.path.join(session['path'],'u_*.pkl'))[0]
    session['b0_path'] = sim
    return bloch_fig()

@bw_app.route('/get_rock_sim', methods=['POST'])
def get_rock_sim():
    data = json.loads(request.data.decode())
    rock_sim = data['sim']
    sims = np.sort(glob.glob(os.path.join(session['path'],'u_*.pkl')))

    i    = max(min(rock_sim,sims.size),1)-1
    sim  = sims[i] #;print(i,sim)
    session['b0_path'] = sim
    session['frame'] = data['frame']
    fig = bloch_fig()
    return json.dumps({'fig':fig, 'sim':i+1})

@bw_app.route('/show_rock', methods=['POST'])
def show_rock():
    data = json.loads(request.data.decode())
    refl = data['refl']
    rock = ut.load_pkl(file=rock_path(session['id']))
    update_rock_thickness()

    df=pd.concat([
        b0.df_G.loc[b0.df_G.index.isin(refl), ['Sw','I']]
            for b0 in map(lambda i:rock.load(i), range(rock.n_simus))
        ])
    df['hkl']=df.index

    ### the figure
    fig = px.line(df,x='Sw',y='I',color='hkl',markers=True)
    fig.update_layout(
        title="Rocking curve at z=%d A" %session['bloch']['thick'],
        hovermode='closest',
        paper_bgcolor="LightSteelBlue",
        xaxis_title='Excitation Error Sw(A^-1)',yaxis_title='Intensity',
        width=fig_wh, height=fig_wh,
    )
    session['graph']='rock'
    return fig.to_json()

@bw_app.route('/update_rock_thickness', methods=['POST'])
def update_rock_thickness():
    rock = ut.load_pkl(file=rock_path(session['id']))
    rock.do('set_thickness',thick=session['bloch']['thick'])

########################
#### Thickness stuffs
########################
@bw_app.route('/update_thickness', methods=['POST'])
def update_thickness():
    thick = json.loads(request.data.decode())['thick']
    b0 = ut.load_pkl(session['b0_path'])
    b0.set_thickness(thick=thick)
    b0.save(session['b0_path'])
    session['bloch']['thick'] = thick
    session['now'] = time.time()
    return bloch_fig()

def update_thicks(thicks):
    thicks = tuple(np.array(b_arr(thicks,(0,100,100)),dtype=int).tolist())
    session['bloch']['thicks'] = thicks
    return thicks


@bw_app.route('/update_refl', methods=['POST'])
def update_refl():
    data=json.loads(request.data.decode())
    session['refl']=data['refl']
    return json.dumps({'refl':session['refl']})

@bw_app.route('/beam_vs_thick', methods=['POST'])
def beam_vs_thick():
    data=json.loads(request.data.decode())
    thicks = update_thicks(data['thicks'])
    b0_path=session['b0_path']
    refl = data['refl']

    b0  = ut.load_pkl(b0_path)
    idx = b0.get_beam(refl=refl)
    b0._set_beams_vs_thickness(thicks=thicks)
    Iz  = b0.get_beams_vs_thickness(idx=idx,dict_opt=True)
    b0.save(get_pkl(session['id']))

    df = pd.DataFrame(columns=['z','I','hkl'])
    # print(Iz.items())
    for hkl,I in Iz.items():
        df_hkl = pd.DataFrame(np.array([b0.z,I]).T,columns=['z','I'])
        df_hkl['hkl'] = hkl
        df = pd.concat([df,df_hkl])
    ### the figure
    fig = px.line(df, x='z', y='I', color='hkl',markers=True)
    fig.update_layout(
        title="thickness dependent intensities",
        hovermode='closest',
        paper_bgcolor="LightSteelBlue",
        width=fig_wh, height=fig_wh,
        xaxis_title='thickness(A)',yaxis_title='intensity',
    )
    session['graph']='thick'
    return fig.to_json()



########################
#### misc
########################
@bw_app.route('/set_fig1', methods=['POST'])
def set_max_res():
    data =json.loads(request.data.decode())
    session['max_res'] = data['max_res']
    session['dq_ring'] = data['dq_ring']
    # print(session['max_res'])
    return bloch_fig()

@bw_app.route('/show_sf', methods=['POST'])
def show_sf():
    b0 = ut.load_pkl(session['b0_path'])
    q  = np.linspace(0,max(session['max_res'],b0.df_G.q.max()),500)
    Z = list(b0.crys.chemical_composition)#;print(Z)
    q,fq = scatf.get_elec_atomic_factors(Z,q)
    cs = dict(zip(Z,dsp.getCs('Spectral',len(Z))))
    cs.update({'H':'#808080','C':'#0f0f0f','N':'blue','O':'red','S':'yellow'})

    fig=go.Figure()
    for fe,Ze in zip(fq,Z):
        fig.add_trace(go.Scatter(
            x=q,y=fe,name=Ze,marker_color=cs[Ze],

        ))

    fig.update_layout(
        title="Electron scattering form factors",
        hovermode='closest',
        paper_bgcolor="LightSteelBlue",
        width=fig_wh, height=fig_wh,
        xaxis_title='q(A^-1)',yaxis_title='fe(A)',
        )
    session['graph']='scat'
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

@bw_app.route('/set_visible', methods=['POST'])
def set_visible():
    data=json.loads(request.data.decode())
    key = data['key']
    session['time']=time.time()
    session['vis'][key]=data['v']
    return json.dumps({key:session['vis'][key]})

@bw_app.route('/set_structure', methods=['POST'])
def set_structure():
    data = request.form
    # data=json.loads(request.data.decode())
    # print(data)
    session['mol']=data['mol']
    init_mol()
    return session['mol']

# def set_manual_mode():
#     # session['modes']['manual'] = True
#     # if session['dat']['pets']:
#     #     session['modes']['manual'] = False
#     # if not session['dat']['pets'] and not session['modes']['manual']:
#     if not session.get('modes'):session.modes={}
#     session['modes']['manual'] = not session['dat']['pets']

############################################################################
#### Init
############################################################################
@login_required
@bw_app.route('/init', methods=['GET'])
def init():
    now = time.time()
    print('username : ' ,session['username'])
    if session.get('id') and os.path.exists(session.get('path')):
        init_mol()
        if (now-session['last_time'])>24*3600:
            print('warning:session created at %s has expired ' %session['last_time'])
            print(check_output('rm -rf %s/*' %session.get('path'),shell=True).decode())
            init_args()
    else:
        id = '%s_%s' %(session['username'],create_id())
        session_path=os.path.join('static','data','tmp',id)
        print(check_output('mkdir -p %s' %session_path,shell=True).decode())
        print(colors.green+'creating new session %s' %id+colors.black)
        session['path'] = session_path
        session['id']   = id
        session['b0_path'] = get_pkl(session['id'])
        if not session.get('mol'):session['mol'] = 'diamond'
        init_session()

    if session['dat']['pets'] and not session['mol'] in pets_data.keys():
        pets_data[session['mol']]=pt.Pets(pets_path(session['mol']),gen=False,dyn=0)
    if session['dat']['felix'] and not session['mol'] in felix_data.keys():
        if os.path.exists(felix_path(session['mol'])):
            felix_data[session['mol']] = fe.load_felix(session['path'])
        else:
            felix_data[session['mol']] = fe.Felix(session['path'],session['mol'])


    rock_state=''
    if len(glob.glob(os.path.join(session['path'],'u_*.pkl')))>0:
        rock_state='done'

    # print('sending init info')
    info=['mol','dat','frame','crys','cif_file',
        'modes','omega','expand','refl','max_res','dq_ring','graph','rings']
    session_data = {k:session[k] for k in info}
    session_data['theta_phi'] = b_str(session['theta_phi'],2)
    session_data['bloch'] = get_session_data('bloch')
    session_data['rock']  = get_session_data('rock')
    session_data['rock_state'] = rock_state
    # exp,sim
    session_data['zmax'] = {}
    session_data['max_frame'] = 0
    if session['sim']:
        session_data['max_frame']   = session['sim']['max_frame']
        session_data['zmax']['sim'] = session['sim']['zmax']
    if session['exp']:
        session_data['max_frame']   = max(session['exp']['max_frame'],session_data['max_frame'])
        session_data['zmax']['exp'] = session['exp']['zmax']
    # print(session_data['max_frame'])

    session_data['structures'] = [s for s in structures if s!=session['mol']]
    session_data['gifs'] = gifs
    return json.dumps(session_data)

def init_session():
    init_mol()
    init_args()

def init_mol():
    mol = session['mol']
    exp = get_frames(mol,'exp')
    sim = get_frames(mol,'sim',d={'offset':10})
    dat = {
        'exp':type(exp)==dict,
        'sim':type(sim)==dict,
        'pets':os.path.exists(os.path.join(mol_path(mol),'pets')),
        'felix':os.path.exists(os.path.join(mol_path(mol),'reflprofiles_strong.dat')),
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

    if not session.get('modes'):session['modes']={'analysis':'bloch'}
    session['modes']['manual'] = not dat['pets']
    if not session.get('frame'):session['frame'] = 1

    now = time.time()
    session['cif_file'] = cif_file
    session['crys']     = crys_dat
    session['dat'] = dat
    session['sim'] = sim
    session['exp'] = exp
    session['zm_counter'] = 0 #dummy variable
    session['time']  = now

def init_args():
    rock_args = {'u0':[0,0,1],'u1':[0.01,0,1],'nframes':3,'show':0}
    bloch_args={
        'keV':200,'u':[0,0,1],
        'Nmax':4,'dmin':1,'gemmi':False,'Smax':0.02,
        'thick':250,'thicks':[0,300,100],'felix':False,'nbeams':200
        }
    felix_args={
        'keV':200,'ww':40,'wid':200,
        'np':4,'jobs_done':'69/69','jobs_run':'','jobs_state':'',
    }
    if not session.get('modes'):session['modes'] = {'analysis' : 'bloch'}
    modes = {
        'molecule'  : False,
        'u'         : 'edit',
        'single'    : False,
        }

    expand_bloch = {'omega':False,'struct':False,'thick':False,
        'refl':False,'sim':False,'u':True,}

    now = time.time()
    # session['mol2']  = mol
    session['dq_ring']  = 0.25
    session['rings']    = []
    session['omega']    = 157 #in-plane rotation angle
    session['max_res']  = 0
    session['expand']   = expand_bloch
    session['modes'].update(modes)
    # session['vis']      = {k:True for k in ['I','Vga','Sw','I_pets','rings']}
    session['vis']      = {'I':True,'Vga':'legendonly','Sw':'legendonly','I_pets':True,'rings':True}
    session['theta_phi']  = [0,0]
    session['bloch']      = bloch_args
    session['felix']      = felix_args
    session['rock']       = rock_args
    session['refl']       = []
    session['graph']      = 'thick'
    session['last_time']  = now
    session['time'] = now



def get_frames(mol,dat,d={}):
    frames = glob.glob(get_path(mol,dat,'*'))
    max_frame=len(frames)
    frames_dict=None
    if max_frame>0:
        pad = len(os.path.basename(frames[0]).replace('.tiff',''))
        frames_dict = {
            'tmp':0,'zmax':50, 'z_max':[50]*max_frame,
            'max_frame':max_frame,'pad':pad
        }
        frames_dict.update(d)
    return frames_dict

def get_session_data(key):
    if key=='bloch':
        data=session['bloch'].copy()
        data.update({'u':b_str(session['bloch']['u'],4),
            'thicks':b_str(session['bloch']['thicks'],0)})
    elif key == 'rock':
        data=session['rock'].copy()
        data.update({
            'u0':b_str(session['rock']['u0'],4),
            'u1':b_str(session['rock']['u1'],4),
        })
    return data
