# import importlib as imp
from subprocess import check_output,Popen,PIPE
import json,tifffile,os,sys,glob,time,datetime
from flask import Flask,Blueprint,request,url_for,redirect,jsonify,session,render_template
import numpy as np,pandas as pd
from functools import wraps
import plotly.express as px
import plotly.graph_objects as go
from utils import glob_colors as colors
from utils import displayStandards as dsp
from blochwave import bloch
from blochwave import bloch_pp as bl            #;imp.reload(bl)
from scattering import scattering_factors as scatf
from EDutils import pets as pt                  #;imp.reload(pt)
from EDutils import utilities as ut             #;imp.reload(ut)
from in_out import*

bloch = Blueprint('bloch', __name__)
pets_data = {}


########################
#### functions
########################
def bloch_fig():
    b0 = load_b0()
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
    session['last_time'] = time.time()

    # print(session['bloch'])
    fig.update_layout(
        title="diffraction pattern z=%d A" %session['bloch']['thick'],
        paper_bgcolor='LightSteelBlue',#cdcfd1',
        # plot_bgcolor ='LightSteelBlue',#79a3f7',
        width=fig_wh, height=fig_wh,
    )
    # fig.update_traces(mode='markers')
    fig.update_xaxes(range=[-xm,xm])
    fig.update_yaxes(range=[xm,-xm])
    return fig.to_json()





@bloch.route('/set_fig1', methods=['POST'])
def set_max_res():
    data =json.loads(request.data.decode())
    session['max_res'] = data['max_res']
    session['dq_ring'] = data['dq_ring']
    # print(session['max_res'])
    return bloch_fig()








########################################################################
########################################################################
#### Bloch
########################################################################
########################################################################
@bloch.route('/update_omega', methods=['POST'])
def update_omega():
    data=json.loads(request.data.decode())
    session['omega']=data['omega']
    # print(data['omega'])
    return bloch_fig()

@bloch.route('/bloch_rotation', methods=['POST'])
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

@bloch.route('/bloch_u', methods=['POST'])
def bloch_u():
    data=json.loads(request.data.decode())
    b_args = data['bloch']
    ## handle
    # print(session['bloch'])
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
    b0 = load_b0()
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
        fig_data = {}#bloch_fig()
    info = json.dumps({'fig':fig_data,'nbeams':b0.nbeams,
        'bloch':bloch_args,'theta_phi':b_str(session['theta_phi'],4)})
    return info

@bloch.route('/solve_bloch', methods=['POST'])
def solve_bloch():

    b0 = load_b0()
    b0.solve(opts='vts',felix=session['bloch']['felix'])#opts=session['bloch']['opts'])
    fig_data = bloch_fig()
    # print(colors.red,session['rings'],colors.black)
    return json.dumps({'rings':session['rings'],'fig':fig_data})

@bloch.route('/show_u', methods=['POST'])
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
@bloch.route('/rock_state', methods=['GET'])
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

@bloch.route('/bloch_state', methods=['GET'])
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

@bloch.route('/set_rock_frame', methods=['POST'])
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

@bloch.route('/set_rock', methods=['POST'])
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

@bloch.route('/solve_rock', methods=['POST'])
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

@bloch.route('/overlay_rock', methods=['POST'])
def overlay_rock():
    sim = glob.glob(os.path.join(session['path'],'u_*.pkl'))[0]
    session['b0_path'] = sim
    return bloch_fig()

@bloch.route('/get_rock_sim', methods=['POST'])
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

@bloch.route('/show_rock', methods=['POST'])
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

@bloch.route('/update_rock_thickness', methods=['POST'])
def update_rock_thickness():
    rock = ut.load_pkl(file=rock_path(session['id']))
    rock.do('set_thickness',thick=session['bloch']['thick'])

########################
#### Thickness stuffs
########################
@bloch.route('/update_thickness', methods=['POST'])
def update_thickness():
    thick = json.loads(request.data.decode())['thick']
    b0 = load_b0()
    b0.set_thickness(thick=thick)
    b0.save(session['b0_path'])
    session['bloch']['thick'] = thick
    session['now'] = time.time()
    return bloch_fig()

def update_thicks(thicks):
    thicks = tuple(np.array(b_arr(thicks,(0,100,100)),dtype=int).tolist())
    session['bloch']['thicks'] = thicks
    return thicks


@bloch.route('/update_refl', methods=['POST'])
def update_refl():
    data=json.loads(request.data.decode())
    session['refl']=data['refl']
    return json.dumps({'refl':session['refl']})

@bloch.route('/beam_vs_thick', methods=['POST'])
def beam_vs_thick():
    data=json.loads(request.data.decode())
    thicks = update_thicks(data['thicks'])
    b0_path=session['b0_path']
    refl = data['refl']

    b0  = load_b0()
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
#### scattering factors
########################
@bloch.route('/show_sf', methods=['POST'])
def show_sf():
    b0 = load_b0()
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






#####################################################
#### MISC
#####################################################
@bloch.route('/set_mode_val', methods=['POST'])
def set_mode_val():
    data = json.loads(request.data.decode())
    session['modes'][data['key']] = data['val']
    # print(colors.red,data['key'],session['modes'][data['key']],colors.black)
    session['last_time']=time.time()
    return 'ok'

@bloch.route('/set_mode_u', methods=['POST'])
def set_mode_u():
    data = json.loads(request.data.decode())
    # print(data)
    key  = data['key']
    session['modes'][key] = data['val']
    session['mol']  = session['mol']
    session['mol']  = data['mod']
    return json.dumps({key:session['modes'][key]})

@bloch.route('/set_visible', methods=['POST'])
def set_visible():
    data=json.loads(request.data.decode())
    key = data['key']
    session['time']=time.time()
    session['vis'][key]=data['v']
    return json.dumps({key:session['vis'][key]})


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



@bloch.route('/init_bloch_panel', methods=['GET'])
def init_bloch_panel():
    if session['new'] :
        rock_args = {'u0':[0,0,1],'u1':[0.01,0,1],'nframes':3,'show':0}
        bloch_args={
            'keV':200,'u':[0,0,1],
            'Nmax':6,'dmin':1,'gemmi':False,'Smax':0.02,
            'thick':250,'thicks':[0,300,100],'felix':False,'nbeams':200
            }
        if not session.get('modes'):
            session['modes'] = {'analysis' : 'bloch'}
        modes = {
            'molecule'  : False,
            'u'         : 'edit',
            'single'    : False,
            }

        expand_bloch = {
            'omega':False,'struct':False,'thick':False,
            'refl':False,'sim':False,'u':True,}

        # session['mol2']  = mol
        session['omega']    = 157 #in-plane rotation angle
        session['expand']   = expand_bloch
        session['modes'].update(modes)
        # session['vis']      = {k:True for k in ['I','Vga','Sw','I_pets','rings']}
        session['theta_phi']  = [0,0]
        session['bloch']      = bloch_args
        session['rock']       = rock_args
        session['dq_ring']  = 0.25
        session['rings']    = []
        session['max_res']  = 0

    vis = {'I':True,
        'Vga':'legendonly','Sw':'legendonly','I_pets':True,
        'rings':True}

    session['graph'] = 'thick'
    session['vis']   = vis
    session['refl']  = []
    # if not session['dat']['pets']:
    #     print(colors.red+'pets not found : setting vis["I_pets"] to false'+colors.black)
    #     session['vis']['I_pets']=False

    rock_state=''
    if len(glob.glob(os.path.join(session['path'],'u_*.pkl')))>0:
        rock_state='done'


    if session['dat']['pets'] and not session['mol'] in pets_data.keys():
        if os.path.exists(os.path.join(mol_path(session['mol']),'pets','reflections.txt')):
            dat_type='dials'
            pets_data[session['mol']]=pt.Dials(dials_path(session['mol']))
        else:
            dat_type='pets'
            pets_data[session['mol']]=pt.Pets(pets_path(session['mol']),gen=False,dyn=0)
        print(colors.red+'found processed data type : %s' %dat_type+colors.black)

    now = time.time()
    session['last_time']  = now
    session['time'] = now

    session_data = {k:session[k] for k in[
        'omega','expand','modes','refl','graph',
        'rings','max_res','dq_ring',
        ]}
    session_data['theta_phi'] = b_str(session['theta_phi'],2)
    session_data['bloch'] = get_session_data('bloch')
    session_data['rock']  = get_session_data('rock')
    session_data['rock_state'] = rock_state
    # print(session['bloch'])

    return json.dumps(session_data)


@bloch.route('/init_bloch', methods=['GET'])
def init_bloch():
    return json.dumps({k:session[k] for k in ['modes']})


def load_b0():
    i,n_try=0,4
    err=1
    while i<n_try and err :
        err=0
        try:
            b0 = ut.load_pkl(session['b0_path'])
        except Exception as err:
            print(colors.red,err,colors.black)
            # if type(e)=EOFError
            time.sleep(0.25)
            # b0 = ut.load_pkl(session['b0_path'])
    return b0
