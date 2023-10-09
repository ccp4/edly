import pytest
from time import sleep
from utils import glob_colors as colors
from selenium.webdriver.common.keys import Keys
from selenium_utils import*

@pytest.mark.lvl1
def test_import_cif(chrome_driver,sec):
    if not chrome_driver.find_element("id", "import_menu_open_btn").is_displayed():
        click(chrome_driver,'expand_import_menu',sec)

    print(colors.green+"\nImport cif "+colors.yellow+cif_path+colors.black,end="")
    click(chrome_driver,'import_menu_cif_btn',sec)
    write(chrome_driver,'input_Cif_file',cif_path,sec)
    click(chrome_driver,'import_cif_file_button',sec)

    print(colors.green+",Check import"+colors.black,end="")
    check_text(chrome_driver,'current_cif_file_div',cif_file)
    click(chrome_driver,'import_menu_open_btn',sec)
    click(chrome_driver,'info_struct_refresh_btn',sec)
    check_text(chrome_driver,'info_struct_cif',cif_file)

    print(colors.green+"done"+colors.black)
    click(chrome_driver,'expand_import_menu',sec)


@pytest.mark.lvl2
def test_import_dat(chrome_driver,sec):
    if not chrome_driver.find_element("id", "import_menu_open_btn").is_displayed():
        click(chrome_driver,'expand_import_menu',sec)
    print(colors.green+"\nImport dat"+colors.black,end="")
    click(chrome_driver,'import_menu_dat_btn',sec)

    for dat_type,dat_file in dat_files.items():
        print(', '+colors.yellow+dat_type+colors.green,end="")
        dat_path = os.path.join(dat_folder,dat_file)
        write(chrome_driver,'input_dat_file',dat_path,sec)
        check_text(chrome_driver,'dat_type_span',dat_type)
        click(chrome_driver,'import_dat_file_btn',sec)


    dat_type='xds'
    print(colors.green+", select and check " +colors.yellow+dat_type+colors.black,end="")
    select_by_text(chrome_driver,'dat_type_select',dat_type,sec)
    click(chrome_driver,'import_menu_open_btn',sec)
    click(chrome_driver,'info_struct_refresh_btn',sec)
    check_text(chrome_driver,'info_struct_dat',dat_type)

    print(colors.green+", done"+colors.black)
    click(chrome_driver,'expand_import_menu',sec)



@pytest.mark.lvl1
def test_bloch_mode(chrome_driver,sec):
    print(colors.green+"\nTesting bloch mode"+colors.black,end="")
    click(chrome_driver,'bloch_tab',sec)
    check_text(chrome_driver,'mode_title_panel','Bloch solver')

@pytest.mark.lvl2
def test_bloch_single(chrome_driver,sec):
    print(colors.blue+", bloch single "+colors.black,end="")
    click(chrome_driver,'u_single',sec)
    click(chrome_driver,'u_edit',sec)
    write(chrome_driver,'u_input','0.1,0.2,1',sec,clear=True)

    print(colors.blue+", solve"+colors.black,end="")
    click(chrome_driver,'solve_btn',2)
    check_text(chrome_driver,'solve_btn','Completed')

    print(colors.blue+", thick"+colors.black,end="")
    thick=550
    write(chrome_driver,'bloch_thick_input',str(thick),sec,clear=True)
    write(chrome_driver,'bloch_thick_input',Keys.ENTER,sec)
    check_plotly_elt_text(chrome_driver,'fig1','gtitle','diffraction pattern z=%d A' %thick)

    #navigate thickness
    # print(colors.blue+", nav thick"+colors.black,end="")
    # click(chrome_driver,'bloch_thick_btn',sec)


    print(colors.blue+", thicks"+colors.black,end="")
    thicks=str((100,550,100))
    write(chrome_driver,'bloch_thicks_input',str(thicks),sec,clear=True)
    write(chrome_driver,'bloch_thicks_input',Keys.ENTER,sec)
    select_by_text(chrome_driver,'graph_select','thickness',sec)
    check_plotly_elt_text(chrome_driver,'fig2','gtitle','thickness dependent intensities')

    print(colors.blue+", done"+colors.black)
    sleep(sec)
