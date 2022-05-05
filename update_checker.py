# Checks SteamCMD to see if any steam games have had updates.
import os
import sys
from datetime import datetime
from datetime import date
from datetime import timedelta
import requests
import xml.etree.ElementTree as ET
import app_info

def get_app_ids(username):
    url = f"https://steamcommunity.com/profiles/{username}/games?tab=all&xml=1"
    headers={
    'cookie':'cf_chl_2=b0a0fb97c1aef6c; cf_chl_prog=x11; cf_clearance=Dg0rX.8dsVgkVTeuu_olEewXrYJWiIgSx1FewQ6uY50-1651099758-0-150; __Host-steamdb=0%3B3726637%3Bd52fde1ca7a5452b281097cdd3c3215d13777644',
    'user-agent':"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36"
    }
    r = requests.get(url,headers=headers)
    if r.status_code != 200:
        print("Error Getting List of App IDs")
        return []
    tree = ET.ElementTree(ET.fromstring(r.text))
    root = tree.getroot()

    if root.find('error') is not None:
        print(root.find('error').text)
        exit(0)

    return {game.find('appID').text: game.find('name').text for game in root.iter('game')}
    

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

# Use SteamDB to look up when the last time a given app was updated.
def get_app_updated_since(appid,app_name,cutoff_date):
   
    last_updated,deps = app_info.get_appid_info(appid)

    print("-------------")
    print(f"[INFO] {app_name} (AppID: {appid})")
    if(deps == None):
        print("ERROR")
        print("-------------")
        return False
    
    print(f"Last Updated: {last_updated}\nDependencies: [{','.join(deps)}]\n")
    if cutoff_date < last_updated:
        print(f"Update Available! {last_updated}")
        print("-------------")
        return True
    print("-------------")
    return False

if __name__=="__main__":
    if len(sys.argv) < 3:
        print(f"Usage {sys.argv[0]} STEAM_PROFILE_ID number_of_days_cutoff (eg 30)")
        exit(-1)

    # Get Cutoff Date
    cutoff = date.today() + timedelta(-int(sys.argv[2]))
    # Get All Apps
    app_db = get_app_ids(sys.argv[1])
    # Check last patch updated for each App.
    for appid in app_db.keys():
        get_app_updated_since(appid,app_db[appid],cutoff)
