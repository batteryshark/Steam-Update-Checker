#r = session.get("https://steamdb.info/app/346110/depots/?branch=public")

import time
import re
import binascii
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from datetime import datetime
import atexit




options = webdriver.ChromeOptions() 
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument("--disable-blink-features=AutomationControlled")

driver = webdriver.Chrome(options=options,executable_path='./chromedriver')

TS_START = "<i>timeupdated:</i> <b>"
TS_END = "</b>"

DEPOTS_START = "<h2>Depots</h2>"
DEPOTS_END = "<h3 id=\"branches\">"

# A bullshit way to pull the last updated value out of an HTML tag.
def extract_date(input_data):
    start_offset = input_data.find("Last Update: <b>")
    if start_offset == -1:
        print("Failed to Find Update Start Token")
        return False,None
    
    start_offset += len("Last Update: <b>")
    end_offset = input_data[start_offset:].find("</b>") + start_offset
    extracted_date = input_data[start_offset:end_offset]
    last_updated = datetime.strptime(extracted_date,"%d %B %Y")
    return True,last_updated
    
def carve_depots_data(data):
    start_loc = data.find(DEPOTS_START)
    if(start_loc < 1):
        print("Carve Depots Failed!")
        return
    start_loc += len(DEPOTS_START)
    end_loc = data[start_loc:].find(DEPOTS_END)
    if(end_loc < 1):
        print("Carve Depots (end) Failed!")
        return
    end_loc+=start_loc
    dfs = pd.read_html(data[start_loc:end_loc])
    return dfs

def get_appid_info(app_id):
    
    # Prime the fucker with our app id for caching
    driver.get("https://steamdb.info")
    driver.add_cookie({'name': 'cf_clearance', 'value': 'PdE0aDbbnACuNSXorsB4nEPNbsFNVNznDoedbik0h_M-1651187195-0-150'})    
    driver.get(f"https://steamdb.info/search/?a=app&q={app_id}")
    data = driver.page_source
    while "App Type" not in data:
        data = driver.page_source
        

    # Get Last Updated timestamp Data
    ts_url = f"https://steamdb.info/api/RenderAppHover/?appid={app_id}"

    driver.get(ts_url)
    data = driver.page_source
    res,last_updated = extract_date(data)
    if(not res):
        print("Extracting Updated Date Failed!")
        print(ts_url)
        return None,None
    # Get Dependency Data

    driver.get(f"https://steamdb.info/app/{app_id}/depots/?branch=public")
    data = driver.page_source    
    
    depots_table = carve_depots_data(data)
    deps = []
    try:
        for d in depots_table:
            for dv in d.values:
                pkg_name = dv[1]
                extra_info = dv[5]
                try:
                    if("Shared Install" in extra_info):
                        deps.append(pkg_name)
                except:
                    continue
    except:
        print("Error Getting Dependencies")
        deps = []
    return last_updated.date(),deps
    

def unload():
    driver.quit()
atexit.register(unload)



if __name__ == "__main__":
    app_id = 346110
    last_updated,deps = get_appid_info(app_id)
    print(f"AppID: {app_id} Last Updated: {last_updated} Deps: [{','.join(deps)}]")
