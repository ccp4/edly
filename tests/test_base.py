import sys,pytest,argparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from time import sleep
from utils import glob_colors as colors

click = lambda d,id:d.execute_script("arguments[0].click();", d.find_element("id",id))

@pytest.fixture(scope="module")
def chrome_driver(pytestconfig):
    options = webdriver.ChromeOptions()
    if pytestconfig.getoption('headless'):
        options.add_argument('headless')

    chrome_driver = webdriver.Chrome(options=options)
    chrome_driver.get('http://%s:%s/viewer' %(
        pytestconfig.getoption('ip'),pytestconfig.getoption('port')))
    if not pytestconfig.getoption('headless'):
        chrome_driver.maximize_window()
    return chrome_driver

@pytest.fixture(scope="module")
def sec(pytestconfig):
    sleep=int(pytestconfig.getoption('sleep'))
    if pytestconfig.getoption('headless'):
        sleep=0
    return sleep

def test_login(chrome_driver,sec):
    print(colors.green+"\nLogin : "+colors.black,end="")
    chrome_driver.find_element("tag name", "input").send_keys('test_bot');sleep(sec)
    chrome_driver.find_element("tag name", "form").submit()
    WebDriverWait(chrome_driver, timeout=10).until(lambda d:d.find_element("id", "u_single"))
    print(colors.green+"done"+colors.black)

def test_gaas(chrome_driver,sec):
    print(colors.green+"\nSelecting gaas structure"+colors.black,end="")
    # gaas_link = chrome_driver.find_element("name", "struct_GaAs")
    # chrome_driver.execute_script("arguments[0].click();", gaas_link)
    # single_mode=WebDriverWait(chrome_driver, timeout=10).until(EC.element_to_be_clickable((By.ID,"u_single")))
    # single_mode=WebDriverWait(chrome_driver, timeout=10).until(lambda d:d.find_element("id", "u_single"))
    print(colors.blue+" ,u vector"+colors.black,end="")
    click(chrome_driver,'u_single')                         ;sleep(sec)
    click(chrome_driver,'u_edit')                           ;sleep(sec)
    u_input = chrome_driver.find_element("id", "u_input")
    u_input.clear();u_input.send_keys('0.1,0.2,1')          ;sleep(sec)

    print(colors.blue+" ,solving"+colors.black,end="")
    click(chrome_driver,'solve_btn')                        ;sleep(sec)
    WebDriverWait(chrome_driver, timeout=10).until(
        lambda d:d.find_element("id", "solve_btn").text=='Completed')
    print(colors.blue+", done"+colors.black)                ;sleep(sec)


def test_close(chrome_driver):
    print(colors.green+"\nclosing browser. Good bye"+colors.black)
    chrome_driver.close()
