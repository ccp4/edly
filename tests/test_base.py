import sys,pytest,argparse,datetime,os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from time import sleep
from utils import glob_colors as colors
from selenium_utils import*

d = datetime.datetime.today()
str_date = d.strftime("%d-%m-%y_%H-%M-%S")
struct_test='bot_test_%s' %str_date
dat_folder=os.path.realpath(os.path.join(os.path.dirname(__file__),
    '../static/spg/'))
rock_name='test_5'

@pytest.fixture(scope="module")
def chrome_driver(pytestconfig):
    options = webdriver.ChromeOptions()
    if pytestconfig.getoption('headless'):
        # options.add_argument("--window-size=1920,1080")
        # options.add_argument("--start-maximized")
        options.add_argument('--headless')

    if pytestconfig.getoption('address'):
        address=pytestconfig.getoption('address')
    else:
        port = pytestconfig.getoption('port')
        ip   = pytestconfig.getoption('ip')
        address = 'http://%s:%s' %(ip,port)
    chrome_driver = webdriver.Chrome(options=options)
    # chrome_driver.set_network_conditions(offline=True,latency=5,throughput=500*1024)
    # print(address)
    chrome_driver.get(address)
    chrome_driver.maximize_window()

    return chrome_driver

@pytest.fixture(scope="module")
def sec(pytestconfig):
    sleep=int(pytestconfig.getoption('sleep'))
    if pytestconfig.getoption('headless'):
        sleep=0
    return sleep


################################################################################
################################################################################
### begin
################################################################################
################################################################################
def test_login(chrome_driver,sec):
    print(colors.green+"\nLogin : "+colors.black,end="")
    chrome_driver.find_element("tag name", "input").send_keys('test_bot')
    chrome_driver.find_element("tag name", "form").submit()
    WebDriverWait(chrome_driver, timeout=10).until(lambda d:d.find_element("id", "expand_import_menu"))
    sleep(1)
    print(colors.green+",done"+colors.black)

################################################################################
################################################################################
### import/upload menu
################################################################################
################################################################################
@pytest.mark.lvl1
def test_new_structure(chrome_driver,sec):
    print(colors.green+"\nCreating structure %s" %struct_test+colors.black,end="")
    sec=0
    click(chrome_driver,'expand_import_menu',sec)
    click(chrome_driver,'import_menu_open_btn',sec)
    click(chrome_driver,'new_struct_btn',sec)
    write(chrome_driver,'input_new_struct_name',struct_test,sec)
    check_text(chrome_driver,'span_new_struct_name',struct_test)
    submit_form(chrome_driver,'form_cif')
    check_text(chrome_driver,'structure_panel_name',struct_test)
    click(chrome_driver,'expand_import_menu',sec)
    sleep(1)
    print(colors.green+",done"+colors.black)

@pytest.mark.lvl2
def test_import_cif(chrome_driver,sec):
    cif_file = 'alpha_glycine.cif'
    cif_path = os.path.join(dat_folder,cif_file)

    print(colors.green+"\nImport cif "+colors.yellow+cif_path+colors.black,end="")
    click(chrome_driver,'expand_import_menu',sec)
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
def test_import_frames(chrome_driver,sec):
    frame='localhost_8020_test'
    print(colors.green+"\nImport frames "+colors.yellow+frame+colors.black,end="")
    click(chrome_driver,'expand_import_menu',sec)
    click(chrome_driver,'import_menu_frames_btn',sec)
    click(chrome_driver,'import_frames_toggle_btn',sec)

    print(colors.green+",Select from local database"+colors.black,end="")
    write(chrome_driver,'search_local_frames',frame,sec,clear=True)
    click(chrome_driver,'li_frames_%s' %frame,sec,exec=False)

    print(colors.green+",Import"+colors.black,end="")
    check_text(chrome_driver,'span_dl_link',frame)
    write(chrome_driver,'search_local_frames',Keys.ESCAPE,sec)
    click(chrome_driver,'import_frames_btn_%s' %frame,sec)
    check_text(chrome_driver,'mode_title_panel',"Frames Viewer")

    print(colors.green+",Check import"+colors.black,end="")
    click(chrome_driver,'import_menu_open_btn',0)
    click(chrome_driver,'info_struct_refresh_btn',sec)
    check_text(chrome_driver,'info_struct_frames',frame)

    print(colors.green+",done"+colors.black)
    click(chrome_driver,'expand_import_menu',sec)

@pytest.mark.lvl2
def test_import_dat(chrome_driver,sec):
    dat_files={
        'xds':'XDS_ASCII.HKL',
        'dials':'dials.zip',
        # 'pets':'pets.zip',
    }
    # fails=['fail_pets.zip','fail_dials.zip']

    print(colors.green+"\nImport dat"+colors.black,end="")
    click(chrome_driver,'expand_import_menu',sec)
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


################################################################################
################################################################################
### frames
################################################################################
################################################################################
@pytest.mark.lvl2
def test_frame_mode(chrome_driver,sec):
    print(colors.green+"\nTesting frames mode"+colors.black,end="")
    click(chrome_driver,'frames_tab',sec)
    check_text(chrome_driver,'mode_title_panel','Frames Viewer')

@pytest.mark.lvl2
def test_frame_click_nav(chrome_driver,sec):
    print(colors.green+", click nav"+colors.black,end="")
    max_frame = int(chrome_driver.find_element('id','max_frame_span').text)
    navs = [('forward',2),('fast_forward',max_frame),('forward',max_frame),
            ('backward',max_frame-1),('fast_backward',1),('backward',1),]
    for (nav,frame) in navs:
        click(chrome_driver,'frames_%s_btn' %nav,sec)
        check_text(chrome_driver,'frame_nb_span',str(frame))

@pytest.mark.lvl2
def test_frame_key_nav(chrome_driver,sec):
    print(colors.green+", key nav"+colors.black,end="")
    keys=[('d',11),('w',12),('s',11),('a',1),('e',1),('d',21),(Keys.BACKSPACE,21),('a',11)]
    click(chrome_driver,'frame_mode_select_btn',sec)
    for (key,frame) in keys:
        write(chrome_driver,'frame_select_span',key,0)
        check_text(chrome_driver,'frame_nb_span',str(frame))
    click(chrome_driver,'frame_mode_select_btn',sec)

@pytest.mark.lvl2
def test_frame_input_nav(chrome_driver,sec):
    print(colors.green+", input nav"+colors.black,end="")
    frame='12'
    write(chrome_driver,'frame_select_input',frame,0,clear=True)
    write(chrome_driver,'frame_select_input',Keys.ENTER,sec)
    check_text(chrome_driver,'frame_nb_span',frame)

@pytest.mark.lvl2
def test_frame_brightness(chrome_driver,sec):
    print(colors.green+", brightness"+colors.black,end="")
    write(chrome_driver,'exp_brightness_input','200',0,clear=True)
    write(chrome_driver,'exp_brightness_input',Keys.ENTER,sec)


@pytest.mark.lvl2
def test_frame_heatmap(chrome_driver,sec):
    print(colors.green+", heatmap"+colors.black,end="")
    select_by_text(chrome_driver,'heatmap_select','Greys_r',sec)
    select_by_text(chrome_driver,'heatmap_select','hot',sec)


################################################################################
################################################################################
### bloch
################################################################################
################################################################################
@pytest.mark.lvl2
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


################################################################################
################################################################################
### clear
################################################################################
################################################################################
@pytest.mark.lvl1
def test_delete_struct(chrome_driver,sec):
    print(colors.green+"\nDeleting structure %s" %struct_test+colors.black,end="")
    if not chrome_driver.find_element("id", "import_menu_open_btn").is_displayed():
        click(chrome_driver,'expand_import_menu',sec)
    click(chrome_driver,'import_menu_open_btn',sec)

    print(colors.green+", Selecting" +colors.black,end="")
    write(chrome_driver,'search_struct',struct_test,sec,clear=True)
    click(chrome_driver,'li_%s' %struct_test,sec,exec=False)
    check_text(chrome_driver,'info_struct_name',struct_test)
    write(chrome_driver,'search_struct',Keys.ESCAPE,1)

    print(colors.green+", Deleting"+colors.black,end="")
    click(chrome_driver,'delete_struct_btn',sec)
    submit_form(chrome_driver,'form_delete')
    check_text(chrome_driver,'info_struct_name',"")

    print(colors.green+", done"+colors.black,end="")
    click(chrome_driver,'expand_import_menu',sec)
    sleep(2)

@pytest.mark.opt
def test_kill(chrome_driver):
    print(colors.green+"\nKilling the server."+colors.black)
    # chrome_driver.get('%s/kill_server' %address)


def test_close(chrome_driver):
    print(colors.green+"\nclosing browser. Good bye"+colors.black)
    chrome_driver.close()
