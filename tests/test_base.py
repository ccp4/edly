import sys,pytest,argparse,datetime,os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from time import sleep
from utils import glob_colors as colors
d = datetime.datetime.today()
str_date = d.strftime("%d-%m-%y_%H-%M-%S")
struct_test='bot_test_%s' %str_date

def click(d,id,sec,exec=True):
    elt = WebDriverWait(d, timeout=3).until(lambda d:d.find_element("id", id))
    if exec:
        d.execute_script("arguments[0].click();", d.find_element("id", id))
    else:
        elt.click()
    sleep(sec)

def focus(d,id,sec):
    elt = WebDriverWait(d, timeout=3).until(lambda d:d.find_element("id", id))
    elt.click()
    sleep(sec)

def clear(d,id):
    elt = WebDriverWait(d, timeout=3).until(lambda d:d.find_element("id", id))
    elt.clear()
def write(d,id,s,sec,clear=False):
    elt = WebDriverWait(d, timeout=3).until(lambda d:d.find_element("id", id))
    # d.execute_script("arguments[0].value='%s';" %s, elt)
    if clear:
        elt.clear()
    elt.send_keys(s)
    sleep(sec)

def check_text(d,id,s):
    WebDriverWait(d, timeout=3).until(lambda d:d.find_element("id", id).text==s)

def submit_form(d,id):
    elt=d.find_element("id", id);
    elt.submit()

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
### tests
################################################################################
################################################################################
def test_login(chrome_driver,sec):
    print(colors.green+"\nLogin : "+colors.black,end="")
    chrome_driver.find_element("tag name", "input").send_keys('test_bot')
    chrome_driver.find_element("tag name", "form").submit()
    WebDriverWait(chrome_driver, timeout=10).until(lambda d:d.find_element("id", "expand_import_menu"))
    sleep(1)
    print(colors.green+",done"+colors.black)

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

def test_import_cif(chrome_driver,sec):
    cif_path=os.path.realpath(
        os.path.join(os.path.dirname(__file__),
        '../test/alpha_glycine.cif'))
    cif_file = os.path.basename(cif_path)

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


def test_import_frames(chrome_driver,sec):
    frame='localhost_8020_test'
    print(colors.green+"\nImport frames "+colors.yellow+frame+colors.black,end="")
    click(chrome_driver,'expand_import_menu',sec)
    click(chrome_driver,'import_menu_frames_btn',sec)
    click(chrome_driver,'import_frames_toggle_btn',sec)

    print(colors.green+",Select from local database"+colors.black,end="")
    write(chrome_driver,'search_local_frames',frame,sec,clear=True)
    click(chrome_driver,'li_frames_%s' %frame,sec,exec=False)
    # sleep(10)

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

# def test_bloch_single(chrome_driver,sec):
#     print(colors.blue+" ,bloch single setup"+colors.black,end="")
#     # click(chrome_driver,'bloch_panel')                      ;sleep(sec)
#     click(chrome_driver,'u_single')                         ;sleep(sec)
#     WebDriverWait(chrome_driver, timeout=10).until(lambda d:d.find_element("id", "solve_btn").text=='Solve')
#     click(chrome_driver,'u_edit')                           ;sleep(sec)
#     u_input=WebDriverWait(chrome_driver, timeout=3).until(EC.presence_of_element_located((By.ID,'u_input')))
#     write(chrome_driver,'u_input','0.1,0.2,1')              ;sleep(sec)
#
#     print(colors.blue+" ,solving"+colors.black,end="")
#     click(chrome_driver,'solve_btn')                        ;sleep(sec)
#     WebDriverWait(chrome_driver, timeout=10).until(
#         lambda d:d.find_element("id", "solve_btn").text=='Completed')
#     print(colors.blue+", done"+colors.black)                ;sleep(sec)
#
#
# def test_rock(chrome_driver,sec):
#     print(colors.green+"\nSelecting rock mode"+colors.black,end="")
#     click(chrome_driver,'u_rock')                         ;sleep(sec)
#     WebDriverWait(chrome_driver, timeout=10).until(lambda d:d.find_element("id", "rock_settings_btn"))
#     click(chrome_driver,'rock_settings_btn')              ;sleep(sec)
#     WebDriverWait(chrome_driver, timeout=10).until(lambda d:d.find_element("id", "rock_name"))
#     click(chrome_driver,'rock_name')                      ;sleep(sec)
#     WebDriverWait(chrome_driver, timeout=10).until(lambda d:d.find_element("id", "input_rock_name"))
#     write(chrome_driver,'input_rock_name','auto_test0')
#     write(chrome_driver,'input_rock_name','auto_test0')
#
#

def test_delete_struct(chrome_driver,sec):
    print(colors.green+"\nDeleting structure %s" %struct_test+colors.black,end="")
    if not chrome_driver.find_element("id", "import_menu_open_btn").is_displayed():
        click(chrome_driver,'expand_import_menu',sec)
    click(chrome_driver,'import_menu_open_btn',sec)

    print(colors.green+",Selecting" +colors.black,end="")
    write(chrome_driver,'search_struct',struct_test,sec,clear=True)
    click(chrome_driver,'li_%s' %struct_test,sec,exec=False)
    check_text(chrome_driver,'info_struct_name',struct_test)
    write(chrome_driver,'search_struct',Keys.ESCAPE,1)

    print(colors.green+",Deleting"+colors.black,end="")
    click(chrome_driver,'delete_struct_btn',sec)
    submit_form(chrome_driver,'form_delete')
    check_text(chrome_driver,'info_struct_name',"")

    print(colors.green+",done"+colors.black,end="")
    click(chrome_driver,'expand_import_menu',sec)
    sleep(2)

def test_close(chrome_driver):
    sleep(3)
    print(colors.green+"\nclosing browser. Good bye"+colors.black)
    chrome_driver.close()
