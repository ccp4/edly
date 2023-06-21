import os,json,time
import numpy as np
import pandas as pd
from utils import glob_colors as colors
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

records_json='static/spg/records.json'

options = webdriver.ChromeOptions()
options.add_argument('--headless')
# options.add_argument("--window-size=1920,1080")
# options.add_argument("--start-maximized")
# browser = webdriver.Firefox(options=options)
browser = webdriver.Chrome()


def get_records():
    browser.get("https://zenodo.org/communities/microed/search?page=1&size=1000")
    elts = browser.find_elements("class name", "record-elem")
    d = {os.path.basename(e.get_dom_attribute("href")): e.text
            for e in map(lambda e: e.find_elements("tag name", "a")[1], elts)}
    # print(d)
    # records = pd.DataFrame.from_dict(d,orient='index',columns=['title'])
    return d


def get_files(records):
    all_files = dict()
    for record in records:
        print(record)
        browser.get("https://zenodo.org/record/%s" %record)
        files = browser.find_element("id", "files").find_elements("tag name", "tr")

        df = pd.DataFrame(columns=['size','link'])
        for file in map(lambda e: e.find_elements("tag name", "td"),files[1:]):
            a = file[0].find_element('tag name','a')
            df.loc[a.text] = [file[1].text,a.get_dom_attribute("href")]
        # print(df)
        all_files[record]=df.to_dict('index')
        time.sleep(np.random.rand()*2)
    return all_files


records = get_records()

with open(records_json,'r') as f:
    all_records = json.load(f)

new_records=np.setdiff1d(
    list(records.keys()),
    list(all_records.keys())
)

if any(new_records):
    print(colors.green,'new records :')
    print(colors.blue, ' '.join(new_records),colors.black)

    new_files = get_files(new_records)

    for record in new_records:
        all_records[record]['files'] = new_files[record]
        all_records[record]['title'] = records[record]

    with open(records_json,'w') as f:
        f.write(json.dumps(all_records))
    print(colors.green,'zenodo updated ',colors.black)
else:
    print(colors.green,'Already up to date with zenodo',colors.black)
browser.quit()
