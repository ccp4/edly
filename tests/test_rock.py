import pytest
from time import sleep
from utils import glob_colors as colors
from selenium.webdriver.common.keys import Keys
from selenium_utils import*

@pytest.mark.lvl2
def test_solve_rock(chrome_driver,sec):
    print(colors.green+"\nTesting solve rock mode"+colors.black,end="")
    click(chrome_driver,'u_rock',sec)

    print(colors.blue+", settings"+colors.black,end="")
    click(chrome_driver,'expand_rock_settings_btn',sec)
    write(chrome_driver,'rock_u0_input','0,0,1',sec,clear=True)
    write(chrome_driver,'rock_u1_input','0.1,0.2,1',sec,clear=True)
    write(chrome_driver,'rock_npts_input','3',sec,clear=True)

    print(colors.blue+", solve"+colors.black,end="")
    click(chrome_driver,'solve_btn',2)
    check_text(chrome_driver,'solve_btn','done')


    print(colors.blue+", saving"+colors.black,end="")
    click(chrome_driver,'rock_name_span',sec)
    write(chrome_driver,'rock_name_input',rock_name,sec,clear=True)
    write(chrome_driver,'rock_name_input',Keys.ENTER,sec)
    click(chrome_driver,'rock_save_btn',sec)


@pytest.mark.lvl2
def test_rock_features(chrome_driver,sec):
    print(colors.green+"\nTesting rock features"+colors.black,end="")
    click(chrome_driver,'u_rock',sec)

    print(colors.blue+", load rock"+colors.black,end="")
    if not chrome_driver.find_element("id", "load_rock_select").is_displayed():
        click(chrome_driver,'expand_load_rock',sec)
    select_by_text(chrome_driver,'load_rock_select',rock_name,sec)
    click(chrome_driver,'load_rock_btn',sec)
    if not chrome_driver.find_element("id", "rock_name_span").is_displayed():
        click(chrome_driver,'expand_rock_settings_btn',sec)
    check_text(chrome_driver,'rock_name_span',rock_name)

    print(colors.blue+", rock curve"+colors.black,end="")
    thick=300
    select_by_text(chrome_driver,'graph_select','rocking curve',sec)
    if not chrome_driver.find_element("id", "bloch_thick_input").is_displayed():
        click(chrome_driver,'expand_bloch_thick_panel',sec)
    write(chrome_driver,'bloch_thick_input',str(thick),sec,clear=True)
    write(chrome_driver,'bloch_thick_input',Keys.ENTER,sec)
    check_plotly_elt_text(chrome_driver,'fig2','gtitle','Rocking curves (simu at z=%d A)'%thick)

    print(colors.blue+", integrate"+colors.black,end="")
    click(chrome_driver,'rock_int_btn',sec)
    select_by_text(chrome_driver,'graph_select','integrated curve',sec)
    check_plotly_elt_text(chrome_driver,'fig2','gtitle','Integrated intensities')
    # select_by_text(chrome_driver,'graph_select','R factor',sec)
    # check_plotly_elt_text(chrome_driver,'fig2','gtitle','R factor')
    # select_by_text(chrome_driver,'graph_select','Io vs Ic',sec)
    # check_plotly_elt_text(chrome_driver,'fig2','gtitle','Iobserved vs Icalc at z=%s')

    # print(colors.blue+", navigate frames"+colors.black,end="")
