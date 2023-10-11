import pytest
from time import sleep
from utils import glob_colors as colors
from selenium.webdriver.common.keys import Keys
from subprocess import check_output
from selenium_utils import*

@pytest.mark.lvl1
def test_import_frames(chrome_driver,sec):
    if not chrome_driver.find_element("id", "import_menu_open_btn").is_displayed():
        click(chrome_driver,'expand_import_menu',sec)

    print(colors.green+"\nImport frames "+colors.yellow+frame+colors.black,end="")
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
    # print_text(chrome_driver,'info_struct_frames')
    check_text(chrome_driver,'info_struct_frames','/'+frame)

    print(colors.green+",done"+colors.black)
    click(chrome_driver,'expand_import_menu',sec)



@pytest.mark.lvl1
def test_frame_mode(chrome_driver,sec):
    print(colors.green+"\nTesting frames mode"+colors.black,end="")
    click(chrome_driver,'frames_tab',sec)
    check_text(chrome_driver,'mode_title_panel','Frames Viewer')

@pytest.mark.lvl1
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



################
#### zenodo bit
################
# @pytest.mark.new
@pytest.mark.lvl3
def test_zenodo_entry(chrome_driver,sec):
    search='lysozyme'
    record='Electron diffraction datasets of hen egg-white lysozyme'
    name="Lys_ED_Dataset_1.tar.gz"
    data_folder="1250447_Lys_ED_Dataset_1/Lys_ED_Dataset_1"
    if not chrome_driver.find_element("id", "import_menu_open_btn").is_displayed():
        click(chrome_driver,'expand_import_menu',sec)

    print(colors.green+",Select from zenodo"+colors.black,end="")
    if not chrome_driver.find_element("id", "search_frames").is_displayed():
        click(chrome_driver,'import_frames_toggle_btn',sec)
    print(colors.green+",pick record : %s" %record+colors.black,end="")
    write(chrome_driver,'search_frames',search,sec,clear=True)
    click(chrome_driver,'li_zenodo_%s' %record,sec,exec=False)

    print(colors.green+",pick first dataset"+colors.black,end="")
    click(chrome_driver,'td_record_%s' %name,sec,exec=False)
    check_text(chrome_driver,'td_frames_folder_%s' %data_folder,data_folder)
    print(colors.green+",done"+colors.black)

def remove_folder(data_folder):
    #### delete folder and reload the page
    folder_path='../static/database/%s' %data_folder
    if os.path.exists(folder_path):
        cmd="rm -rf %s" %folder_path
        check_output(cmd,shell=True)

# @pytest.mark.new
@pytest.mark.lvl3
def test_zenodo_download(chrome_driver,sec,address):
    #http://localhost:8020/frames_test.zip
    link="%s/frames_test.zip" %address
    data_folder="localhost_8020_frames_test"
    remove_folder(data_folder)

    print(colors.green+"\nDownload_test "+colors.yellow+data_folder+colors.black,end="")
    chrome_driver.get(address)

    print(colors.green+", Setting link"+colors.black,end="")
    if not chrome_driver.find_element("id", "input_download_link").is_displayed():
        click(chrome_driver,'download_link_btn',sec,exec=False)
    write(chrome_driver,'input_download_link',link,sec,clear=True)
    click(chrome_driver,'download_link_btn',sec,exec=False)

    print(colors.green+", Downloading"+colors.black,end="")
    click(chrome_driver,'btn_download',sec,exec=False)
    # sleep(0.1)

    print(colors.green+", Cancelling download"+colors.black,end="")
    click(chrome_driver,'btn_cancel_download',sec,exec=False)

    print(colors.green+", Re Downloading"+colors.black,end="")
    click(chrome_driver,'btn_download',sec,exec=False)
    check_text(chrome_driver,'td_frames_folder_%s' %data_folder,data_folder)
    print(colors.green+",download complete"+colors.black,end="")

    # remove_folder(data_folder)
