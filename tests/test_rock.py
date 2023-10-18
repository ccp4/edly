import pytest
from time import sleep
from utils import glob_colors as colors
from selenium.webdriver.common.keys import Keys
from selenium_utils import*

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

def solve_rock(chrome_driver,sec,rock_name):
    print(colors.blue+", new rock %s" %rock_name + colors.black,end="")
    click(chrome_driver,'new_rock_btn',sec)
    if chrome_driver.find_element("id", "rock_name_input").is_displayed():
        click(chrome_driver,'rock_name_input',sec)
    write(chrome_driver,'rock_name_input',rock_name,sec,clear=True)#,exec=True)
    write(chrome_driver,'rock_name_input',Keys.ENTER,sec)
    check_text(chrome_driver,'rock_name_span',rock_name)
    write(chrome_driver,'rock_u0_input','0,0,1',sec,clear=True)
    write(chrome_driver,'rock_u1_input','0.1,0.2,1',sec,clear=True)
    write(chrome_driver,'rock_npts_input','3',sec,clear=True)

    print(colors.blue+", solve"+colors.black,end="")
    sleep(0.2)
    click(chrome_driver,'solve_btn',2)
    check_text(chrome_driver,'solve_btn','done')

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


# @pytest.mark.new
@pytest.mark.lvl1
def test_solve_rock(chrome_driver,sec):
    print(colors.green+"\nTesting solve rock mode"+colors.black,end="")
    init_rock(chrome_driver,sec)
    solve_rock(chrome_driver,sec,rock_name)
    save_rock(chrome_driver,sec,rock_name)
    print(colors.blue+", done"+colors.black)

# @pytest.mark.new
@pytest.mark.lvl2
def test_load_rock(chrome_driver,sec):
    print(colors.green+" Testing load rock"+colors.black,end="")
    click(chrome_driver,'u_rock',sec)

    if not chrome_driver.find_element("id", "load_rock_select").is_displayed():
        click(chrome_driver,'expand_load_rock',sec)
    select_by_text(chrome_driver,'load_rock_select',rock_name,sec)
    click(chrome_driver,'load_rock_btn',sec)
    check_text(chrome_driver,'rock_name_span',rock_name)
    print(colors.blue+", done"+colors.black)


@pytest.mark.lvl2
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


# @pytest.mark.new
@pytest.mark.lvl2
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


# @pytest.mark.new
@pytest.mark.lvl3
def test_autosave_rock(chrome_driver,sec):
    rock_name="new_rock_test"

    print(colors.green+"\nTesting autosave rock"+colors.black,end="")
    solve_rock(chrome_driver,sec,rock_name)

    print(colors.blue+", new rock without saving"+ colors.black,end="")
    click(chrome_driver,'new_rock_btn',sec)
    click_elt_form(chrome_driver,'yes',sec)
    check_saved_rock(chrome_driver,sec,rock_name)
