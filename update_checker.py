# Checks SteamDB to see if any steam games have had updates.
import os
import sys
from datetime import datetime
from datetime import date
from datetime import timedelta
import requests
import xml.etree.ElementTree as ET


def get_app_ids(username):
    url = f"https://steamcommunity.com/profiles/{username}/games?tab=all&xml=1"
    r = requests.get(url)
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
    headers = {
        'x-requested-with': 'XMLHttpRequest',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.54 Safari/537.36',
    }       

    url = f"https://steamdb.info/api/RenderAppHover/?appid={appid}"

    r = requests.get(url,headers=headers)
    if r.status_code != 200:
        print(f"[Error] URL: {url} returned {r.status_code}")
        print(r.content)
        return False

    res,last_updated = extract_date(r.content.decode('utf-8'))
    if res is False:
        return False
    
    if cutoff < last_updated.date():
        print(f"[INFO] Update Available for: {app_name} (AppID: {appid}): {last_updated.date()}")
        return True
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
