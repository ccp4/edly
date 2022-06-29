# import importlib as imp
from subprocess import check_output,Popen,PIPE
import json,tifffile,os,sys,glob
from flask import Flask,Blueprint,request,url_for,redirect,jsonify,session,render_template
from EDutils import felix as fe              #;imp.reload(fe)
import plotly.express as px
import plotly.graph_objects as go
from in_out import*


felix = Blueprint('felix', __name__)


@felix.route('/show_felix_rock', methods=['POST'])
def show_felix_rock():
    data = json.loads(request.data.decode())
    refl = data['felix_refl']
    f = fe.load_felix(felix_path(session['path']))
    df = f.df_peak.loc[refl]

    fig=go.Figure()
    fig.add_trace(go.Scatter(
        x=df.r,y=df.I,name=refl,marker_color='b',
        ))

    fig.update_layout(
        title="Experimental rocking curve",
        hovermode='closest',
        paper_bgcolor="LightSteelBlue",
        width=fig_wh, height=fig_wh,
        xaxis_title='Frame',yaxis_title='Intensity',
        )
    session['graph']='felix_rock'
    return fig.to_json()
