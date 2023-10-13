import pytest
from time import sleep
from utils import glob_colors as colors
from selenium.webdriver.common.keys import Keys
from selenium_utils import*


@pytest.mark.lvl1
def test_bloch_single(chrome_driver,sec):
    print(colors.green+"\nTesting bloch single mode"+colors.black,end="")
    print(colors.blue+", check cif"+colors.black,end="")
    check_cif(chrome_driver,sec)

    print(colors.blue+", bloch single "+colors.black,end="")
    click(chrome_driver,'bloch_tab',sec)
    check_text(chrome_driver,'mode_title_panel','Bloch solver')
    click(chrome_driver,'u_single',sec)
    click(chrome_driver,'u_edit',sec)
    write(chrome_driver,'u_input','0.1,0.2,1',sec,clear=True)

    print(colors.blue+", solve"+colors.black,end="")
    sleep(0.2)
    click(chrome_driver,'solve_btn',2)
    check_text(chrome_driver,'solve_btn','Completed')

@pytest.mark.lvl2
def test_bloch_thick(chrome_driver,sec):
    print(colors.blue+", thick"+colors.black,end="")
    thick=550
    if not chrome_driver.find_element("id", "bloch_thick_input").is_displayed():
        click(chrome_driver,'expand_bloch_thick_panel',sec)

    write(chrome_driver,'bloch_thick_input',str(thick),sec,clear=True)
    write(chrome_driver,'bloch_thick_input',Keys.ENTER,sec)
    check_plotly_elt_text(chrome_driver,'fig1','gtitle','diffraction pattern z=%d A' %thick)

    print(colors.blue+", thicks"+colors.black,end="")
    thicks=str((100,550,100))
    write(chrome_driver,'bloch_thicks_input',str(thicks),sec,clear=True)
    write(chrome_driver,'bloch_thicks_input',Keys.ENTER,sec)
    select_by_text(chrome_driver,'graph_select','thickness',sec)
    check_plotly_elt_text(chrome_driver,'fig2','gtitle','thickness dependent intensities')

    print(colors.blue+", done"+colors.black)
    sleep(sec)
