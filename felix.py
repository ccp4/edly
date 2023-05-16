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

# felix_data = {}

def get_form(request):
    return json.loads(request.data.decode())


def plot_rock(refl):
    f = load_felix(session)
    fig=go.Figure()
    if refl in f.df_peak.index:
        tle ="Experimental rocking curve for : %s " %refl
        df = f.df_peak.loc[refl]
        fig.add_trace(go.Scatter(
            x=df.f,y=df.I,name=refl,marker_color='blue',
            ))
    else:
        tle='%s not found in exp refls' %refl

    fig.update_layout(
        title=tle,
        hovermode='closest',
        paper_bgcolor="LightSteelBlue",
        width=fig_wh, height=fig_wh,
        xaxis_title='Frame',yaxis_title='Intensity',
        )
    # session['felix_graph']='felix_rock'
    return fig.to_json()

def plot_lacbed(refl):
    f = load_felix(session)
    r = f.df_sims.loc[f.df_sims.refl==refl]
    if r.shape[0]==0:
        # new_refl = f.df_sims.refl.values[0]
        tle='%s not found in sim refls.' %(refl)
        fig=go.Figure()
        fig.update_layout(
            title=tle,
            hovermode='closest',
            paper_bgcolor="LightSteelBlue",
            width=fig_wh, height=fig_wh,
            xaxis_title='px',yaxis_title='py',
            )
        # tle+=' Setting refl to  %s' %new_refl
        print(colors.red+'warning:%s' %tle +colors.black)
        return fig.to_json()
        # refl = new_refl
        # session['refl'] = refl
        # r = f.df_sims.loc[f.df_sims.refl==refl]
    elif r.shape[0]>1:
        print(colors.red+'warning:more than 1 instance of refl %s' %refl+colors.black)
    r = r.iloc[0]
    I = np.reshape(np.fromfile(r.file,
        dtype=np.float64),(int(r.nwx),)*2)
    fig = px.imshow(I,color_continuous_scale='gray', origin='lower')
    fig.update_layout(
        title="Simulated lacbed curve for : %s at %s in sim %s" %(refl,r.thick, r.sim),
        hovermode='closest',
        paper_bgcolor="LightSteelBlue",
        width=fig_wh, height=fig_wh,
        xaxis_title='px',yaxis_title='py',
        )
    # session['felix_graph']='felix_lacbed'
    # print('completed...')
    return fig.to_json()

def lacbed_png(refl):
    png_paths = os.path.join(mol_path(session['mol']),
        'plots','*%s*.png' %refl)
    lacbed_imgs = glob.glob(png_paths)
    if len(lacbed_imgs):
        lacbed_img = lacbed_imgs[0]
    else :
        lacbed_img = 'static/images/dummy.png'
    return lacbed_img


################################################
#### calls
################################################

@felix.route('/show_lacbed', methods=['POST'])
def show_lacbed():
    form=get_form(request) #;print(form)
    refl,png = [ form[c] for c in ['refl','png']]
    # print(colors.red,png,colors.black)
    if png:
        return lacbed_png(refl)
    else:
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



@felix.route('/init_felix', methods=['POST'])
def init_felix():
    session_data = {'felix':False}
    if os.path.exists(felix_path(session['mol'])):
        f = load_felix(session)
        exp_refls = list(f.df_refl.index.unique())# [s[1:-1].replace(' ','') for s in f.df_refl.index.values]
        erefl = exp_refls[0]
        sim_refls,srefl,fig2 = [],'',{}
        is_sim = 'df_sims' in f.__dict__.keys()
        if is_sim:
            i=0
            sim_refls = list(f.df_sims.refl.unique())
            while exp_refls[i] not in sim_refls:
                i+=1
            erefl = exp_refls[i]
            srefl = sim_refls[i]
            fig2 = plot_lacbed(srefl)
        # print(refl)
        session_data = {
            'exp_refls':exp_refls,'sim_refls':sim_refls,
            'refls':{'e':erefl,'s':srefl},
            # 'fig1':plot_rock(erefl),
            # 'fig2':fig2,
            'is_sim':is_sim,'felix':True,
            }
    return json.dumps(session_data)


@felix.route('/init_felix_panel', methods=['POST'])
def init_felix_panel():
    # if not session['mol'] in felix_data.keys():
    #     if not os.path.exists(felix_pkl(session['mol'])):
    #         felix_data[session['mol']] = fe.load_felix(session['path'])
    #     else:
    # if not os.path.exists(felix_pkl(session['mol'])):
    #
    #         felix_path = os.path.join(session['mol'],'pets')
    #         print(felix_path,glob.glob(felix_path+'/*.dyn.cif_pets'))
    #         felix_data[session['mol']] = fe.Felix(felix_path,session['mol'])

    felix_args={
        'keV':200,'ww':40,'wid':200,
        'np':4,'nodes':20,
        'jobs_done':'69/69','jobs_run':'none','jobs_state':'none',
    }
    session['felix'] = felix_args
    return json.dumps({'felix':session['felix']})
