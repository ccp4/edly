import pytest
from time import sleep
from utils import glob_colors as colors
from selenium.webdriver.common.keys import Keys
from selenium_utils import*

# @pytest.mark.new
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

@pytest.mark.new
def test_close(chrome_driver):
    print(colors.green+"\nclosing browser. Good bye"+colors.black)
    chrome_driver.close()
