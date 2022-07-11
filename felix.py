# import importlib as imp
from subprocess import check_output,Popen,PIPE
import json,tifffile,os,sys,glob
from flask import Flask,Blueprint,request,url_for,redirect,jsonify,session,render_template
from functools import wraps
import plotly.express as px
import plotly.graph_objects as go
from utils import glob_colors as colors
from in_out import*


felix = Blueprint('felix', __name__)

def get_form(request):
    return json.loads(request.data.decode())


def plot_rock(refl):
    f = load_felix(session)
    df = f.df_peak.loc[refl]

    fig=go.Figure()
    fig.add_trace(go.Scatter(
        x=df.f,y=df.I,name=refl,marker_color='blue',
        ))

    fig.update_layout(
        title="Experimental rocking curve for : %s " %refl,
        hovermode='closest',
        paper_bgcolor="LightSteelBlue",
        width=fig_wh, height=fig_wh,
        xaxis_title='Frame',yaxis_title='Intensity',
        )
    session['felix_graph']='felix_rock'
    return fig.to_json()

def plot_lacbed(refl):
    f = load_felix(session)
    r = f.df_sims.loc[f.df_sims.refl==refl]
    if r.shape[0]==0:
        new_refl = f.df_sims.refl.values[0]
        print(colors.red+'warning:%s not found in sims. Setting refl to  %s' %(refl,new_refl) +colors.black)
        refl = new_refl
        session['refl'] = refl
        r = f.df_sims.loc[f.df_sims.refl==refl]
    elif r.shape[0]>1:
        print(colors.red+'warning:more than 1 instance of refl %s' %refl+colors.black)
    r = r.iloc[0]
    I = np.reshape(np.fromfile(r.file,
        dtype=np.float64),(int(r.nwx),)*2)

    fig=px.imshow(I,color_continuous_scale='gray', origin='lower')
    fig.update_layout(
        title="Simulated lacbed curve for : %s at %s in sim %s" %(refl,r.thick, r.sim),
        hovermode='closest',
        paper_bgcolor="LightSteelBlue",
        width=fig_wh, height=fig_wh,
        xaxis_title='px',yaxis_title='py',
        )
    session['felix_graph']='felix_lacbed'
    # print('completed...')
    return fig.to_json()




################################################
#### calls
################################################
@felix.route('/init_felix_panel', methods=['POST'])
def init_felix_panel():
    felix_args={
        'keV':200,'ww':40,'wid':200,
        'np':4,'nodes':20,
        'jobs_done':'69/69','jobs_run':'none','jobs_state':'none',
    }
    session['felix'] = felix_args
    return json.dumps({'felix':session['felix']})


@felix.route('/init_felix', methods=['POST'])
def init_felix():
    f = load_felix(session)
    exp_refls = list(f.df_refl.index.unique())# [s[1:-1].replace(' ','') for s in f.df_refl.index.values]
    sim_refls = list(f.df_sims.refl.unique())
    erefl = exp_refls[0]
    srefl = sim_refls[0]
    # print(refl)
    session_data = {
        'exp_refls':exp_refls,'sim_refls':sim_refls,
        'refls':{'e':erefl,'s':srefl},
        'fig1':plot_rock(erefl),
        'fig2':plot_lacbed(srefl),
        }
    return json.dumps(session_data)

@felix.route('/show_lacbed', methods=['POST'])
def show_lacbed():
    refl = get_form(request)['refl']
    # print(refl)
    return json.dumps({
        'refl':session['refl'],
        'fig':plot_lacbed(refl),
        })

@felix.route('/show_felix_rock', methods=['POST'])
def show_felix_rock():
    # data = get_form(request)
    # refl = data['felix_refl']
    # return plot_rock(refl)
    return plot_rock(get_form(request)['refl'])

@felix.route('/gen_felix', methods=['POST'])
def gen_felix():
    data = get_form(request)
    # print(data)
    return 'ok'
