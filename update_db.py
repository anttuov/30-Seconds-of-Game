# Gets all video ids from a playlist to external sqlite database for easier management

import sqlite3
import requests
import json
from secrets import *

playlist_id = "UUVi6ofFy7QyJJrZ9l0-fwbQ"

def add_url(url, conn):
    c = conn.cursor()
    values = (url, 0)
    try:
        c.execute(f"INSERT INTO playlist VALUES (?,?)", values)
        
    except sqlite3.Error as e:
        print(f"Error inserting value to db: {e}")
    
            

conn = sqlite3.connect("playlist.db")
c = conn.cursor()
table_string = f"""CREATE TABLE IF NOT EXISTS playlist (
                url TEXT NOT NULL UNIQUE,
                used INT NOT NULL);"""

c.execute(table_string)

table_string = f"""CREATE TABLE IF NOT EXISTS uploads (
                url TEXT NOT NULL UNIQUE,
                title TEXT NOT NULL,
                filename TEXT NOT NULL,
                used INT NOT NULL,
                time TIMESTAMP DEFAULT CURRENT_TIMESTAMP);"""

c.execute(table_string)

url = "https://www.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxResults=50&playlistId={}&key={}".format(playlist_id, api_key)

nextpage_exists = True
a = 0
while nextpage_exists:
    r = requests.get(url)
    data = json.loads(r.content)
    try:
        nextpage = data["nextPageToken"]
    except:
        nextpage_exists = False
    items = data["pageInfo"]["totalResults"]
    for item in data["items"]:
        a += 1
        try:
            add_url(item["contentDetails"]["videoId"], conn)
        except:
            print(item, "not video?")
    print("processed", a, " items")
    conn.commit()
    url = "https://www.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxResults=50&playlistId={}&key={}&pageToken={}".format(playlist_id, api_key, nextpage)
conn.close()