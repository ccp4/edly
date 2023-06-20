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


########################
#### functions
########################
def bloch_fig():
    is_dat = session['dat']['pets']
    is_px = session['bloch_modes']['is_px'] and is_dat
    if is_dat:
        pets = pets_data[session['mol']]
    xm = session['max_res']

    fig=go.Figure()

    b0 = load_b0()
    is_sim='df_G' in b0.__dict__
    if is_sim:
        toplot=b0.df_G[['px','py','I','Vga','Sw']].copy()
        if not xm:
            xm = b0.df_G.q.max()#;print('xm set to ',xm)
            xr,yr=[-xm,xm],[xm,-xm]

        ##########################
        #### plot simulation data
        ##########################
        if is_px:
            df_pxy = pets.hkl_to_pixels(toplot.index.tolist(),session['frame'])
            toplot['px']=df_pxy['px']
            toplot['py']=df_pxy['py']

        plts = {
            'I'  :['Ix','blue' ,'circle'     ],
            'Vga':['Vx','green','triangle-up'],
            'Sw' :['Sx','red'  ,'diamond'    ],
        }
        toplot['Ix']=normalize( np.log10(np.maximum(abs(toplot['I'])  ,1e-5)))
        toplot['Vx']=normalize( np.log10(np.maximum(abs(toplot['Vga']),1e-5)))
        toplot['Sx']=normalize(-np.log10(np.maximum(abs(toplot['Sw']) ,1e-5)))
        toplot.index.name='miller indices'


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

    ########################
    #### add exp data
    ########################
    if is_dat:
        pets = pets_data[session['mol']]
        df_pets = pets.rpl.loc[pets.rpl.eval('(F==%d) & (I>2)' %session['frame'])]
        df_pets = df_pets.loc[~(df_pets.hkl == str((0,0,0)))]
        pt_plot=df_pets[['px','py','qx','qy','I','hkl','F']].copy()
        px,py='qx','qy'
        if is_px:px,py='px','py'
        pt_plot['Ix']=normalize(np.log10(np.maximum(abs(pt_plot['I']),1e-2)))

        fig.add_trace(go.Scatter(
            x=pt_plot[px],y=pt_plot[py],marker_size=pt_plot['Ix'],
            name='I_exp',
            visible=session['vis']['I_pets'],
            hovertext=['I_exp']*len(pt_plot),
            marker_symbol='square',marker_color='purple',
            customdata=np.array([pt_plot['I'].values, pt_plot['hkl'].to_numpy()]).T,
            hovertemplate='<b>%{hovertext}</b><br><br>rpx=%{x}<br>rpy=%{y}<br>value=%{customdata[0]:.2f}<br>miller indices=%{customdata[1]}<extra></extra>',
            mode='markers',
        ))
        if is_px:
            x_m,y_m = pets.nxy #pt_plot['px'].max() #*np.sqrt(2)
            xr,yr=[0,x_m],[0,y_m]
            if session['bloch_modes']['reversed']:yr=[y_m,0]
        else:
            if not xm:
                xm=pt_plot[[px,py]].abs().max().max()#;print('xm set to ',xm)
                xr,yr=[-xm,xm],[xm,-xm]

    if is_dat or is_sim:
        # print(is_dat,is_sim)
        ########################
        #### resolution rings
        ########################
        dq_ring = session['dq_ring']
        rings=[]
        if dq_ring:
            t,qs = np.linspace(0,2*np.pi,100),np.arange(dq_ring,xm,dq_ring)
            qr=qs
            ct,st = np.cos(t),np.sin(t)
            rx = lambda r:r*ct; ry=lambda r:r*st
            if is_px:
                # cx,cy = pets.cen.loc[session['frame']-1, ['px','py']]
                if is_sim:
                    cx,cy = toplot.loc[str((0,0,0)),['px','py']]
                else:
                    cx,cy=np.array(pets.nxy)/2
                qr = qs/(pets.aper*np.sqrt(2))
                rx = lambda r:r*ct+cx ;ry = lambda r:r*st+cy

            # print('qs : ',qs)
            for q0,r0 in zip(qs,qr):
                name='%.2f A' %(1/q0)
                fig.add_trace(go.Scatter(
                    x=rx(r0),y=ry(r0),
                    legendgroup="resolution rings",
                    legendgrouptitle_text="res rings",
                    name=name,hovertext=['q=%.3f recA' %q0]*t.size,
                    hovertemplate='<b>ring</b><br>%{hovertext}<br>res='+name+'<extra></extra>',
                    visible=session['vis']['rings'],
                    mode='lines',marker_color='purple',
                ))
            offset=3*is_sim+session['dat']['pets']
            rings=list(range(offset,offset+qs.size))
        session['rings']=rings              #;print('rings',rings)
        session['last_time'] = time.time()


        ########################
        #### layout
        ########################
        # print(session['bloch'])
        fig.update_layout(
            title="diffraction pattern z=%d A" %session['bloch']['thick'],
            paper_bgcolor='LightSteelBlue',#cdcfd1',
            # plot_bgcolor ='LightSteelBlue',#79a3f7',
            width=fig_wh, height=fig_wh,
        )
        # fig.update_traces(mode='markers')
        fig.update_xaxes(range=xr,scaleratio=1)
        fig.update_yaxes(range=yr,scaleratio=1,autorange=False) #[False,"reversed"][session['bloch_modes']['reversed']])
    return fig.to_json()


@bloch.route('/set_max_res_rings', methods=['POST'])
def set_max_res_rings():
    data =json.loads(request.data.decode())
    session['max_res'] = data['max_res']
    session['dq_ring'] = data['dq_ring']
    # print(session['max_res'])
    fig_data = bloch_fig()
    return json.dumps({'rings':session['rings'],'fig':fig_data})

@bloch.route('/update_bloch_frame', methods=['POST'])
def update_bloch_frame():
    data =json.loads(request.data.decode())
    # print(data)
    session['frame'] = data['frame']
    return bloch_fig()

########################################################################
########################################################################
#### Bloch
########################################################################
########################################################################
@bloch.route('/update_omega', methods=['POST'])
def update_omega():
    data=json.loads(request.data.decode())
    session['dat']['omega']=float(data['omega'])
    print('omega updated to %.1f' %session['dat']['omega'])
    return bloch_fig()

@bloch.route('/bloch_rotation', methods=['POST'])
def bloch_rotation():
    data=json.loads(request.data.decode())
    theta,phi = data['theta_phi']
    theta %=180
    phi   %=360
    session['bloch']['u'] = list(ut.u_from_theta_phi(theta,phi))
    # session['bloch']['solve'] = False
    session['bloch_modes']['u'] = 'move'
    # session['bloch_modes']['manual'] = True
    return update_bloch()

@bloch.route('/get_u', methods=['POST'])
def get_u_exp():
    frame = json.loads(request.data.decode())
    u = pets_data[session['mol']].uvw0[frame-1]
    return b_str(u,4)

@bloch.route('/bloch_u', methods=['POST'])
def bloch_u():
    data=json.loads(request.data.decode())#;print(data)
    b_args = data['bloch']
    session['b0_path'] = get_pkl(session['id'])
    ## handle
    thicks = update_thicks(data['bloch']['thicks'])
    keV = session['bloch']['keV']
    # print(session['bloch_modes'])
    if session['bloch_modes']['u0']=='auto' and session['dat']['pets']:
        keV = np.round(pets_data[session['mol']].keV) #;print('recover wavelength %.1f' %keV)
        u = pets_data[session['mol']].uvw0[data['frame']-1]
    else:
        # print(data['bloch']['u'])
        u = b_arr(data['bloch']['u'],session['bloch']['u'])
    # print(data['frame'],u)

    b_args.update({'u':list(u),'thicks':list(thicks),'keV':keV})
    session['frame'] = data['frame']
    # session['bloch_modes']['manual'] = data['manual_mode']
    session['bloch'] = b_args
    # print(session['bloch'])
    # session['last_req'] = 'solve_bloch:%s' %(time.time())
    # print({k:type(v) for k,v in session['bloch'].items()})
    return update_bloch(fig=False)

def update_bloch(fig=True):
    b_args = session['bloch']#.copy()
    # print(b_args['u'])
    # b_args['thicks']=None
    session['b0_path'] = get_pkl(session['id'])
    b0 = load_b0()
    b0.update(**b_args)
    # b0.save()
    session['theta_phi'] = list(ut.theta_phi_from_u(b_args['u']))
    bloch_args=b_args.copy()
    bloch_args.update({'u':b_str(b_args['u'],4),'thicks':b_str(b_args['thicks'],0)})
    info = {'nbeams':b0.nbeams,'bloch':bloch_args,
        'theta_phi':b_str(session['theta_phi'],4)}
    if fig:
        if session['bloch']['felix']:
            fig_data=go.Figure().to_json()
        else:
            fig_data = bloch_fig()
        info['fig'] = fig_data
    return json.dumps(info)

@bloch.route('/solve_bloch', methods=['POST'])
def solve_bloch():
    b0 = load_b0()
    b0.solve(opts='vts',felix=session['bloch']['felix'])#opts=session['bloch']['opts'])
    fig_data = bloch_fig()
    # print(colors.red,session['rings'],colors.black)
    idx = b0.get_beam(refl=session['refl'])
    session['refl'] = b0.df_G.iloc[idx].index.tolist()

    return json.dumps({'rings':session['rings'],'refl':session['refl'],
        'fig':fig_data})

@bloch.route('/show_u', methods=['POST'])
def show_u():
    data = json.loads(request.data.decode())
    if session['bloch_modes']['u']=='rock':
        r_args = get_rock(data)
        uvw = ut.get_uvw_cont(**r_args)
    else:
        if session['bloch_modes']['u0']=='auto':
            uvw = pets_data[session['mol']].uvw0
        else:
            uvw = np.array(b_arr(data['u'],session['bloch']['u']))[None,:]

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

@bloch.route('/get_bloch_sim', methods=['POST'])
def get_bloch_sim():
    session['b0_path'] = get_pkl(session['id'])
    b0 = load_b0()
    return json.dumps({'fig':bloch_fig(),'u':b_str(b0.u,4)})
##############################
#### Rocking curve stuffs
##############################
@bloch.route('/load_rock', methods=['POST'])
def load_rock_data():
    data = json.loads(request.data.decode())#;print(data)
    session['rock_name']=data['rock_name']
    rock = load_rock()
    session['rock'] = {'u0':rock.df.u[0].tolist(),'u1':rock.df.u[-1].tolist(),'nframes':rock.df.shape[0]}
    session['bloch_modes']['integrated']='df_int' in rock.__dict__
    nbs = '%d-%d' %(rock.df.nbeams.min(),rock.df.nbeams.max())

    return json.dumps({'rock':get_session_data('rock'),'nbeams':nbs,
        'modes':session['bloch_modes']})

@bloch.route('/save_rock', methods=['POST'])
def save_rock_data():
    data = json.loads(request.data.decode())#;print(data)
    session['rock_name']=data['rock_name']
    rocks_dir='static/data/%s/rocks' %session['mol']
    if not os.path.exists(rocks_dir):
        check_output('mkdir %s' %rocks_dir,shell=True,).decode()
    rock_dir = os.path.join(rocks_dir,session['rock_name'])
    msg='already exists'
    if not os.path.exists(rock_dir):
        cmd = 'mkdir %s;' %(rock_dir)
        cmd+= 'mv %s/rock_.pkl %s;'%(session['path'],rock_dir)
        cmd+= 'mv %s/u*.pkl %s;'%(session['path'],rock_dir)
        msg=check_output(cmd,shell=True,).decode()
        rock=load_rock()
        rock.change_path(rock_dir)
    rock_names = [os.path.basename(s) for s in glob.glob(os.path.join(sim_path(session['mol']),'*'))]
    return json.dumps({'msg':msg,'rock_names':rock_names})

@bloch.route('/rock_state', methods=['GET'])
def rock_state():
    if not session['rock_state'] == 'done':
        n_simus=len(glob.glob(os.path.join(session['path'],'u_*.pkl')))
        npts=session['rock']['nframes']
        if not n_simus==npts:
            session['rock_state'] = '%d/%d' %(n_simus+1,npts)
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
    opt = data['opt']
    if opt==-1:
        session['rock_frames']=[-1]*2
        return ''
    else:
        frame = max(0,data['frame']-1)
        uvw = pets_data[session['mol']].uvw0
        if opt==0:
            e0 = uvw[frame]
            e1 = np.array(session['rock']['u1'])
            session['rock_frames'][0]=frame
        elif opt==1:
            e0 = np.array(session['rock']['u0'])
            e1 = uvw[frame]
            session['rock_frames'][1]=frame
        elif opt==2:
            session['rock_frames']=[0,uvw.shape[0]]
            e0 = uvw[0] #max(0,frame-2)]
            e1 = uvw[-1]#frame-1]
            # u0 = uvw[max(0,frame-2)]
            # u1 = uvw[frame-1]
            # u2 = uvw[min(frame,frame-1)]
            # e0 = (u0 + u1)/2
            # e1 = (u1 + u2)/2
            # e0/=np.linalg.norm(e0)
            # e1/=np.linalg.norm(e1)

        session['frame'] = frame
        # print(session['rock_frames'])
        session['rock'].update({'u0':e0.tolist(),'u1':e1.tolist()})
        return json.dumps({'rock':get_session_data('rock')})

@bloch.route('/init_rock', methods=['POST'])
def init_rock():
    data=json.loads(request.data.decode())
    r_args = get_rock(data)

    cmd = 'rm %s/u_*.pkl %s' %(session['path'],rock_path(session['id']))
    p=Popen(cmd,shell=True,stderr=PIPE,stdout=PIPE)
    print(p.communicate())

    session['rock_state'] = 'init'
    session['bloch_modes']['integrated'] = False
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
    Sargs['cif_file'] = session['crys']['cif_file']

    uvw  = ut.get_uvw_cont(**session['rock'])
    # print(session['rock'],uvw)
    rock = bl.Bloch_cont(path=session['path'],tag='',uvw=uvw,Sargs=Sargs)
    session['rock_state'] = 'done'
    nbs = '%d-%d' %(rock.df.nbeams.min(),rock.df.nbeams.max())
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
    rock = load_rock()
    i = max(min(rock_sim,rock.df.shape[0]),1)-1
    sim_file = rock.df.pkl[i]
    # sims = #np.sort(glob.glob(os.path.join(session['path'],'u_*.pkl')))
    # sim  = sims[i] #;print(i,sim)
    session['b0_path'] = sim_file
    session['frame']   = data['frame']
    b0 = load_b0()
    u = b0.u

    fig = bloch_fig()
    return json.dumps({'fig':fig, 'u':b_str(u,4),'sim':i+1})

@bloch.route('/show_rock', methods=['POST'])
def show_rock():
    data = json.loads(request.data.decode())
    refl = data['refl']
    tle = "Rocking curves "
    rock=load_rock()
    fig=go.Figure()
    if rock:
        rock_x = data['rock_x']
        rock = load_rock()
        update_rock_thickness()
        df = pd.DataFrame()
        rock_frames=session['rock_frames']
        # print(rock_frames)
        for i in range(rock.n_simus):
            b0       = rock.load(i)
            df0      = b0.df_G.loc[b0.df_G.index.isin(refl), ['Sw','I']].copy()
            df0['i'] = i
            df0['F'] = rock_frames[0] + (rock_frames[1] -rock_frames[0])*i/(rock.n_simus-1)
            df=pd.concat([df,df0])
        df['hkl']=df.index
        fig = px.line(df,x=rock_x,y='I',color='hkl',markers=True)
        tle+="(simu at z=%d A)" %session['bloch']['thick']

    if session['bloch_modes']['exp_rock'] :
        rock_x='F'
        df = load_pets().rpl[['hkl','F','I']]
        df = df.loc[df.hkl.isin(refl)]
        fig = px.line(df,x='F',y='I',color='hkl',markers=True)


    x_axis = {'Sw':'Excitation Error Sw(A^-1)','F':'Frame','i':'rock simulation index'}
    fig.update_layout(
    title=tle,
    hovermode='closest',
    paper_bgcolor="LightSteelBlue",
    xaxis_title=x_axis[rock_x],yaxis_title='Intensity',
    width=fig_wh, height=fig_wh,
    )

    session['graph']='rock'
    session['bloch_modes']['rock_x'] = rock_x
    return fig.to_json()

@bloch.route('/update_rock_thickness', methods=['POST'])
def update_rock_thickness():
    rock = load_rock()
    rock.do('set_thickness',thick=session['bloch']['thick'])

@bloch.route('/show_integrated', methods=['POST'])
def show_integrated():
    data = json.loads(request.data.decode())
    refl = data['refl']
    rock = load_rock()
    df = rock.df_int.loc[refl].transpose()
    df.index=rock.z
    fig = px.line(df,markers=True)

    fig.update_layout(
        title="Integrated intensities",
        hovermode='closest',
        paper_bgcolor="LightSteelBlue",
        xaxis_title='z(Angstrom)',yaxis_title='Integrated Intensity',
        width=fig_wh, height=fig_wh,
    )
    session['graph']='int'
    return fig.to_json()

@bloch.route('/integrate_rock', methods=['POST'])
def integrate_rock():
    if not session['bloch_modes']['integrated']:
        rock = load_rock()
        thicks=session['bloch']['thicks']
        rock.set_beams_vs_thickness(thicks)
        rock.integrate();
        if session['dat']['pets']:
            rock.Rfactor(load_pets().hkl);
        session['bloch_modes']['integrated']=True
    return 'done'

@bloch.route('/show_graph', methods=['POST'])
def show():
    data = json.loads(request.data.decode())
    graph=data['graph']
    if graph=='Rfactor':
        fig=show_Rfactor()
    elif graph=='FovsFc':
        fig=show_FovsFc(data['thick'])
    session['graph']=graph
    return fig.to_json()

def show_Rfactor():
    rock = load_rock()
    # z,R = rock.z,rock.R
    fig = px.line(rock.R[1:],markers=True)
    fig.update_layout(
        title="R factor",
        hovermode='closest',
        paper_bgcolor="LightSteelBlue",
        xaxis_title='z(Angstrom)',yaxis_title='',
        width=fig_wh, height=fig_wh,
    )
    return fig

def show_FovsFc(thick):
    df_exp = load_pets().hkl
    rock = load_rock()

    z0 = rock.df_int.columns[abs(rock.z-thick).argmin()]        #;print(z0)
    refl = rock.df_int.loc[rock.df_int.index.isin(df_exp.index)].index

    I_exp = df_exp.loc[refl,'I'].values
    I_sim = rock.df_int.loc[refl,z0].values
    # print(I_sim.shape,I_exp.shape)
    fig = px.scatter(I_sim,I_exp)#,markers=True)

    fig.update_layout(
        title="Iobserved vs Icalc at z=%s" %z0 ,
        hovermode='closest',
        paper_bgcolor="LightSteelBlue",
        xaxis_title='I_calc',yaxis_title='I_obs',
        width=fig_wh, height=fig_wh,
    )
    return fig

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
    ###get valid reflections
    if not data['clear']:
        b0 = load_b0()
        idx = b0.get_beam(refl=session['refl'])#;print(session['refl'])
        refl = b0.df_G.iloc[idx].index.tolist()#;print(refl)
        session['refl'] = refl
    return json.dumps({'refl':session['refl']})

@bloch.route('/beam_vs_thick', methods=['POST'])
def beam_vs_thick():
    data=json.loads(request.data.decode())
    thicks = update_thicks(data['thicks'])
    refl = data['refl']

    b0  = load_b0()
    idx = b0.get_beam(refl=refl)
    b0._set_beams_vs_thickness(thicks=thicks)
    Iz  = b0.get_beams_vs_thickness(idx=idx,dict_opt=True)
    # b0.save(get_pkl(session['id']))
    b0.save()

    df = pd.DataFrame(columns=['z','I','hkl'])
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

@bloch.route('/to_shelx', methods=['POST'])
def to_shelx():
    thick = session['bloch']['thick']
    output_file_shelx = f"shelx_thick_{thick}A.hkl"
    file = os.path.join(session['path'], output_file_shelx)

    rock = load_rock()
    df = rock.integrate(thick)
    hkl = pd.DataFrame(index=df.index,
        columns=['h','k','l','I','sig'])
    # hkl['I'] = rock.df_int['%.1fA' %thick].values
    hkl[['h','k','l']]=[list(eval(h)) for h in hkl.index]
    hkl['I'] = df['I']*1000
    hkl['sig'] = 0.01
    ut.to_shelx(hkl,file)
    return json.dumps({'hkl_file':file})


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
    # print(data)
    key  = data['key']
    bloch_modes = session['bloch_modes'].copy()
    bloch_modes[key] = data['val']
    session['bloch_modes'] = bloch_modes
    # print(data,data['val'],session['bloch_modes'])
    session['last_time']=time.time()
    if session['bloch_modes']['u']=='single':
        session['b0_path'] = get_pkl(session['id'])
        # print(session['b0_path'])
    return json.dumps(session['bloch_modes'])

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
    session['b0_path']=get_pkl(session['id'])
    b0 = load_b0()
    b1,b2,b3 = np.array(b0.crys.reciprocal_vectors)/(2*np.pi)
    cell_diag = 1/np.linalg.norm(b1+b2+b3) #Angstrom
    rock_names = [os.path.basename(s) for s in glob.glob(os.path.join(sim_path(session['mol']),'*'))]

    # print('cell_diag %1f Angstrom' %cell_diag)
    if session['new'] :
        print(colors.green+'new session'+colors.black)
        rock_args = {'u0':[0,0,1],'u1':[0.01,0,1],'nframes':3,'show':0}
        bloch_args={
            'keV':200,'u':[0,0,1],
            'Nmax':6,'gemmi':False,'Smax':0.015,
            'thick':250,'thicks':[0,300,100],'felix':False,'nbeams':200
            }
        bloch_args['dmin']=cell_diag/bloch_args['Nmax']
        bloch_modes = {
            'u0'        : 'auto'    ,#auto,edit,rotate
            'u'         : 'rock'    ,#single,rock,lacbed
            'single'    : False     ,
            'is_px'     : True      ,
            'reversed'  : False     ,
            'rock_x'    : 'i'       ,#Sw,F,i
            'exp_rock'  : False     ,
            'integrated': False     ,
            }
        vis = {'I':True,
            'Vga':'legendonly','Sw':'legendonly','I_pets':True,
            'rings':True}

        session['bloch_modes'] = bloch_modes
        # session['vis']      = {k:True for k in ['I','Vga','Sw','I_pets','rings']}
        session['theta_phi']   = [0,0]
        session['bloch']       = bloch_args
        session['rock']        = rock_args
        session['dq_ring']     = 0.5
        session['rings']       = []
        session['max_res']     = 0
        session['pred_info']   = True # use dials predicted refl
        session['graph']       = 'thick'
        session['rock_frames'] = [-1,-1]
        session['rock_name']   = "test_5" #"test%d" %len(rock_names)
        session['vis']         = vis

    #reinit on refresh
    expand_bloch = {
        'struct':False,'thick':False,
        'refl':True,'sim':False,'u':True,'load_rock':False}
    # vis = {'I':True,
    #     'Vga':'legendonly','Sw':'legendonly','I_pets':True,
    #     'rings':True}
    rock_axis={'excitation error':'Sw','rock index':'i'};
    if session['dat']['pets']:
        rock_axis['exp frames']='F'


    #### sanity checks on refresh
    rock_state=''
    if len(glob.glob(os.path.join(session['path'],'u_*.pkl')))>0:
        rock_state='done'

    if session['graph']=='rock' and not session['bloch']['u']=='rock':
        session['graph']=='thick'
    if session['graph']=='int' and not session['bloch']['u']=='rock':
        session['graph']=='thick'
    if session['bloch_modes']['u0']=='auto' and not session['dat']['pets']:
        session['bloch_modes']['u0'] = 'edit'
    if session['bloch_modes']['exp_rock'] and not session['dat']['rock']:
        session['bloch_modes']['exp_rock'] = False


    now = time.time()
    # session['vis']       = vis
    session['expand']    = expand_bloch
    session['refl']      = []
    session['last_time'] = now
    session['time'] = now
    session_data = {k:session[k] for k in[
        'expand','bloch_modes','refl','graph',
        'rings','max_res','dq_ring','rock_name',
        ]}
    session_data['theta_phi'] = b_str(session['theta_phi'],2)
    session_data['bloch'] = get_session_data('bloch')
    session_data['rock']  = get_session_data('rock')
    session_data['rock_state'] = rock_state
    session_data['exp_rock']   = session['dat']['rock']
    session_data['exp_refl']   = session['dat']['pets']
    session_data['cell_diag']  = cell_diag
    session_data['rock_axis']  = rock_axis
    session_data['rock_names'] = rock_names
    # print('init bloch:',session['bloch_modes'])
    # print(session['rock_name'])
    return json.dumps(session_data)



@bloch.route('/init_done', methods=['GET'])
def init_done():
    color=colors.__dict__[ {True:'green',False:'red'}[session['init']] ]
    print(colors.blue,'main init done : ',color,session['init'],colors.black)
    return json.dumps(session['init'])


def load_b0():
    try:
        b0 = ut.load_pkl(session['b0_path'])
    except Exception as err:
        print(session['b0_path'])
        print(colors.red,err,colors.black)
        # if type(e)=EOFError
        time.sleep(1)
        b0 = ut.load_pkl(session['b0_path'])

    return b0

def load_rock():
    file='static/data/%s/rocks/%s/rock_.pkl' %(session['mol'],session['rock_name'])
    if not os.path.exists(file):
        file = rock_path(session['id'])
    if os.path.exists(file):
        return ut.load_pkl(file=file)

def load_pets():
    return pets_data[session['mol']]
