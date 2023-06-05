#Implementation of Selenium WebDriver with Python using PyTest

import pytest
from selenium import webdriver
import sys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from time import sleep
from utils import glob_colors as colors

chrome_driver = webdriver.Chrome()
chrome_driver.get('http://localhost:8020/viewer')
chrome_driver.maximize_window()

# chrome_driver=login()

def test_login():
    print(colors.green+"testing login"+colors.black)
    chrome_driver.find_element("tag name", "input").send_keys('test_bot')
    sleep(1)
    chrome_driver.find_element("tag name", "form").submit()
    sleep(3)

def test_gaas():
    print(colors.green+"testing selecting gaas structure"+colors.black)
    gaas_link = chrome_driver.find_element("name", "struct_GaAs")
    chrome_driver.execute_script("arguments[0].click();", gaas_link)
    sleep(2)
    print(colors.blue+"\tspecifying a u vector"+colors.black)
    chrome_driver.find_element("id", "u_single").click()
    sleep(1)
    chrome_driver.find_element("id", "u_edit").click()
    sleep(1)
    u_input = chrome_driver.find_element("id", "u_input")
    u_input.clear()
    u_input.send_keys('0.1,0.2,1')
    sleep(2)
    print(colors.blue+"\tsolving"+colors.black)
    chrome_driver.find_element("id", "solve_btn").click()
    sleep(3)


def test_close():
    print(colors.green+"closing window. Good bye"+colors.black)
    chrome_driver.close()
