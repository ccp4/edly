from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from time import sleep

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
