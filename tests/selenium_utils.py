import os,datetime
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from utils import glob_colors as colors
from subprocess import check_output
from time import sleep

d = datetime.datetime.today()
str_date = d.strftime("%d-%m-%y_%H-%M-%S")
struct_test='bot_test_%s' %str_date
# struct_test='new_test'
dat_folder=os.path.realpath(os.path.join(os.path.dirname(__file__),
    '../static/spg/'))
rock_name='test_3pts'
frame='frames_test'
cif_file = 'alpha_glycine.cif'
cif_path = os.path.join(dat_folder,cif_file)
dat_files={
    'xds':'XDS_ASCII.HKL',
    'dials':'dials.zip',
    # 'pets':'pets.zip',
}
# fails=['fail_pets.zip','fail_dials.zip']

def remove_data_folder(data_folder):
    ''' delete folder and reload the page'''
    folder_path='../static/database/%s' %data_folder
    if os.path.exists(folder_path):
        cmd="rm -rf %s" %folder_path
        check_output(cmd,shell=True)
    return os.path.exists(folder_path)

################################################################################
################################################################################
#### widget interaction
################################################################################
################################################################################
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
def write(d,id,s,sec,clear=False,exec=False):
    elt = WebDriverWait(d, timeout=3).until(lambda d:d.find_element("id", id))
    if exec:
        # elt.click()
        d.execute_script("arguments[0].value='%s';" %s, elt)
    else:
        if clear:
            d.execute_script("arguments[0].value='';", elt)
        #### Note : for some reason there are input for which elt.clear()
        #### results in the element being removed
        #     elt.clear()
        elt.send_keys(s)
    sleep(sec)

def check_text(d,id,s):
    try:
        WebDriverWait(d, timeout=3).until(lambda d:d.find_element("id", id).text==s)
    except Exception as e:
        if d.find_element("id", id).is_displayed():
            print('\n')
            print('expected text :%s' %s)
            print('actual text : %s' %d.find_element("id", id).text)
        raise Exception(e)

def get_elt_txt(d,id):
    return d.find_element("id", id).text
def get_elt(d,id):
    return d.find_element("id", id)

def print_text(d,id):
    print(get_elt_txt(d,id))

def check_plotly_elt_text(d,id,classname,s):
    # print(d.find_element('id',id).find_element("class name", classname).text)
    WebDriverWait(d, timeout=3).until(
        lambda d:d.find_element('id',id).find_element("class name", classname).text==s)

def submit_form(d,id):
    elt=d.find_element("id", id);
    elt.submit()


def select_by_text(d,id,text,sec):
    select=Select(d.find_element('id',id))
    select.select_by_visible_text(text)
    sleep(sec)

def get_elt_style(d,id):
    # elt = d.find_element("id", id)
    return dictify_style(get_elt(d,id).get_attribute("style"))

def dictify_style(style_str):
    style=style_str.strip().split(";")[:-1]
    style_dict={item[0].strip(): item[1].strip() for item in
        map(lambda s: s.split(":"), style)}
    return style_dict

def check_prop_val(d,id,prop,val):
    style=get_elt_style(d,id)
    if prop in style.keys():
        # print(style_dict)
        return style[prop]==val
    else:
        return False

def check_elt_style(d,id,prop,val):
    try:
        WebDriverWait(d, timeout=3).until(lambda d:check_prop_val(d,id,prop,val))
    except Exception as e:
        if d.find_element("id", id).is_displayed():
            print('\n')
            print('expected style value :%s' %val)
            print('actual text : %s' %get_elt_style(d,id)[prop])
        raise Exception(e)


################################################################################
################################################################################
#### utils
################################################################################
################################################################################
def select_frames(chrome_driver,sec):
    if not chrome_driver.find_element("id", "import_menu_open_btn").is_displayed():
        click(chrome_driver,'expand_import_menu',sec)
    click(chrome_driver,'import_menu_frames_btn',sec)


def import_cif(chrome_driver,sec):
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

def check_cif(chrome_driver,sec):
    if not chrome_driver.find_element("id", "cif_file_div").is_displayed():
        click(chrome_driver,'expand_structure_panel',sec)
    cif_file=get_elt_txt(chrome_driver,"cif_file_div")#;print("'%s'" %cif_file)
    if cif_file=='?':
        import_cif(chrome_driver,sec)
    click(chrome_driver,'expand_structure_panel',sec)


def import_dat(chrome_driver,sec):
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
