import pytest
from time import sleep
from utils import glob_colors as colors
from selenium.webdriver.common.keys import Keys
from selenium_utils import*

@pytest.mark.lvl1
def test_import_cif(chrome_driver,sec):
    import_cif(chrome_driver,sec)


@pytest.mark.lvl3
def test_import_dat(chrome_driver,sec):
    import_dat(chrome_driver,sec)
