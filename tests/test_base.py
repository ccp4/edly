import sys,pytest,argparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from time import sleep
from utils import glob_colors as colors


click = lambda d,id:d.execute_script("arguments[0].click();", d.find_element("id",id))
write = lambda d,id,s:d.execute_script("arguments[0].value='%s';" %s, d.find_element("id",id))

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

def test_login(chrome_driver,sec):
    print(colors.green+"\nLogin : "+colors.black,end="")
    chrome_driver.find_element("tag name", "input").send_keys('test_bot');sleep(sec)
    chrome_driver.find_element("tag name", "form").submit()
    # WebDriverWait(chrome_driver, timeout=10).until(lambda d:d.find_element("id", "frames_panel"))
    WebDriverWait(chrome_driver, timeout=10).until(lambda d:d.find_element("id", "u_single"))
    print(colors.green+"done"+colors.black)

def test_gaas(chrome_driver,sec):
    print(colors.green+"\nSelecting gaas structure"+colors.black,end="")
    # click(chrome_driver,'struct_GaAs')                      ;sleep(sec)
    # bloch_panel=WebDriverWait(chrome_driver, timeout=3).until(lambda d:d.find_element("id", "bloch_panel"))

    print(colors.blue+" ,bloch setup"+colors.black,end="")
    # click(chrome_driver,'bloch_panel')                      ;sleep(sec)
    click(chrome_driver,'u_single')                         ;sleep(sec)
    WebDriverWait(chrome_driver, timeout=10).until(lambda d:d.find_element("id", "solve_btn").text=='Solve')
    click(chrome_driver,'u_edit')                           ;sleep(sec)
    u_input=WebDriverWait(chrome_driver, timeout=3).until(EC.presence_of_element_located((By.ID,'u_input')))
    write(chrome_driver,'u_input','0.1,0.2,1')          ;sleep(sec)

    print(colors.blue+" ,solving"+colors.black,end="")
    click(chrome_driver,'solve_btn')                        ;sleep(sec)
    WebDriverWait(chrome_driver, timeout=10).until(
        lambda d:d.find_element("id", "solve_btn").text=='Completed')
    print(colors.blue+", done"+colors.black)                ;sleep(sec)


def test_close(chrome_driver):
    sleep(2)
    print(colors.green+"\nclosing browser. Good bye"+colors.black)
    chrome_driver.close()
