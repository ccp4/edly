import importlib as imp
import pytest
from time import sleep
from utils import glob_colors as colors
from selenium.webdriver.common.keys import Keys
from selenium_utils import*
import selenium_utils;imp.reload(selenium_utils)
from selenium import webdriver

dat_folder='data/'
rock_name='test_1-3'


def test_import_cif(chrome_driver,sec,cif_path):
    selenium_utils.import_cif(chrome_driver,sec,cif_path)

def test_import_xds(chrome_driver,sec,dat_path):
    if not chrome_driver.find_element("id", "import_menu_open_btn").is_displayed():
        click(chrome_driver,'expand_import_menu',sec)
    print(colors.green+"\nImport dat"+colors.black,end="")
    click(chrome_driver,'import_menu_dat_btn',sec)

    dat_type='xds'
    print(colors.green,'import xds',end="")
    write(chrome_driver,'input_dat_file',dat_path,sec)
    check_text(chrome_driver,'dat_type_span',dat_type)
    click(chrome_driver,'import_dat_file_btn',sec)


    print(colors.green,'ckeck correct import',end="")
    select_by_text(chrome_driver,'dat_type_select',dat_type,sec)
    click(chrome_driver,'import_menu_open_btn',sec)
    click(chrome_driver,'info_struct_refresh_btn',sec)
    check_text(chrome_driver,'info_struct_dat',dat_type)

    print(colors.green+", done"+colors.black)
    click(chrome_driver,'expand_import_menu',sec)



def init_rock(chrome_driver,sec):
    print(colors.blue+", check cif"+colors.black,end="")
    check_cif(chrome_driver,sec)
    if chrome_driver.find_element("id", "import_menu_open_btn").is_displayed():
        click(chrome_driver,'expand_import_menu',sec)
    if chrome_driver.find_element("id", "cif_file_div").is_displayed():
        click(chrome_driver,'expand_structure_panel',sec)

    click(chrome_driver,'bloch_tab',sec)
    check_text(chrome_driver,'mode_title_panel','Bloch solver')
    click(chrome_driver,'u_rock',sec)

def check_saved_rock(chrome_driver,sec,rock_name):
    check_elt_style(chrome_driver,'rock_save_btn','background-color','green')
    # sleep(0.5)
    if not chrome_driver.find_element("id", "load_rock_select").is_displayed():
        click(chrome_driver,'expand_load_rock',sec)
    select_by_text(chrome_driver,'load_rock_select',rock_name,sec)
    click(chrome_driver,'load_rock_btn',sec)
    select_by_text(chrome_driver,'load_rock_select',rock_name,sec)

def save_rock(chrome_driver,sec,rock_name):
    print(colors.blue+", saving"+colors.black,end="")
    click(chrome_driver,'rock_save_btn',sec)
    check_saved_rock(chrome_driver,sec,rock_name)

def solve_rock(chrome_driver,sec,rock_name):
    print(colors.blue+", new rock %s" %rock_name + colors.black,end="")
    click(chrome_driver,'new_rock_btn',sec)
    if chrome_driver.find_element("id", "rock_name_input").is_displayed():
        click(chrome_driver,'rock_name_input',sec)
    write(chrome_driver,'rock_name_input',rock_name,sec,clear=True)#,exec=True)
    write(chrome_driver,'rock_name_input',Keys.ENTER,sec)
    check_text(chrome_driver,'rock_name_span',rock_name)

    write(chrome_driver,'frame_select_input','1',sec,clear=True)
    write(chrome_driver,'frame_select_input',Keys.ENTER,sec)
    click(chrome_driver,'rock_u0_btn',sec)
    write(chrome_driver,'frame_select_input','3',sec,clear=True)
    write(chrome_driver,'frame_select_input',Keys.ENTER,sec)
    write(chrome_driver,'rock_npts_input','2',sec,clear=True)
    click(chrome_driver,'rock_u1_btn',sec)

    print(colors.blue+", solve"+colors.black,end="")
    sleep(0.2)
    click(chrome_driver,'solve_btn',2)
    check_text(chrome_driver,'solve_btn','done')


def test_solve_rock(chrome_driver,sec):
    print(colors.green+"\nTesting solve rock mode"+colors.black,end="")
    init_rock(chrome_driver,sec)
    solve_rock(chrome_driver,sec,rock_name)
    save_rock(chrome_driver,sec,rock_name)
    print(colors.blue+", done"+colors.black)

def test_load_rock(chrome_driver,sec):
    print(colors.green+" Testing load rock"+colors.black,end="")
    click(chrome_driver,'u_rock',sec)

    if not chrome_driver.find_element("id", "load_rock_select").is_displayed():
        click(chrome_driver,'expand_load_rock',sec)
    select_by_text(chrome_driver,'load_rock_select',rock_name,sec)
    click(chrome_driver,'load_rock_btn',sec)
    check_text(chrome_driver,'rock_name_span',rock_name)
    print(colors.blue+", done"+colors.black)


def test_rocking_curve(chrome_driver,sec):
    print(colors.green+"\nTesting rocking curve"+colors.black,end="")

    thick=300
    select_by_text(chrome_driver,'graph_select','rocking curve',sec)
    if not chrome_driver.find_element("id", "bloch_thick_input").is_displayed():
        click(chrome_driver,'expand_bloch_thick_panel',sec)
    write(chrome_driver,'bloch_thick_input',str(thick),sec,clear=True)
    write(chrome_driver,'bloch_thick_input',Keys.ENTER,sec)
    check_plotly_elt_text(chrome_driver,'fig2','gtitle','Rocking curves (simu at z=%d A)'%thick)

    print(colors.blue+", done"+colors.black)

def test_integrate(chrome_driver,sec):
    print(colors.blue+", integrate"+colors.black,end="")
    click(chrome_driver,'rock_int_btn',sec)
    select_by_text(chrome_driver,'graph_select','integrated curve',sec)
    # check_plotly_elt_text(chrome_driver,'fig2','gtitle','Integrated intensities')
    # select_by_text(chrome_driver,'graph_select','R factor',sec)
    # check_plotly_elt_text(chrome_driver,'fig2','gtitle','R factor')
    # select_by_text(chrome_driver,'graph_select','Io vs Ic',sec)
    # check_plotly_elt_text(chrome_driver,'fig2','gtitle','Iobserved vs Icalc at z=%s')

    # print(colors.blue+", navigate frames"+colors.black,end="")

    print(colors.blue+", done"+colors.black)
