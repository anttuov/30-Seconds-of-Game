# Downloads and cuts the videos

import sqlite3
from requests import get
import shutil
from subprocess import check_output
import time
import random
import os
import string
import sys
import re

clip_amount = 100
conn = sqlite3.connect("playlist.db")
c = conn.cursor()


def select_random():
    """Select random video from database and mark it as used"""

    print("selecting random video")
    videoid = c.execute('SELECT url FROM playlist WHERE used=0 ORDER BY RANDOM() LIMIT 1').fetchone()[0]
    c.execute('UPDATE playlist SET used=1 WHERE url=?', (videoid,))
    conn.commit()
    vid_url = "https://www.youtube.com/watch?v="+videoid
    return (check_output(["youtube-dl", "-f", "18", "-g", "-e", "--get-duration", vid_url]).decode("utf-8").split("\n"))+[vid_url]


def process_title(title):
    """Clean up the title"""

    good_title = False
    removewords = {"Misc ": "-", "Longplay": "-", "QuickLook": "", "Quicklook": "", "LongPlay": "-"}
    title = re.sub("[\(\[].*?[\)\]]", "", title)
    for word, new in removewords.items():
        if word in title:
            good_title = True
            title = title.replace(word, new).strip()
            title = title.replace("  ", " ")
    if good_title:
        return title
    else:
        return "skip"


def download_video(out):
    """Downloads first 100MB of video to temp.mp4"""

    valid_chars = "-_.()[] %s%s" % (string.ascii_letters, string.digits)
    filename = ''.join(c for c in title if c in valid_chars)+".mp4"
    url = out[1].strip()
    duration = out[2].strip().split(":")
    duration = [int(i) for i in duration]

    if len(duration) == 3:
        duration_sec = duration[0]*60*60+duration[1]*60+duration[2]
    elif len(duration) == 2:
        duration_sec = duration[0]*60+duration[1]
    print("Downloading", title, "Length", duration_sec)
    headers = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.117 Safari/537.36', "Range": "bytes=0-100000000","Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8","Accept-Encoding": "gzip, deflate, br","Accept-Language": "en-US,en;q=0.9,fi;q=0.8,vi;q=0.7", "Cache-Control": "max-age=0", "Connection": "keep-alive", "Upgrade-Insecure-Requests": "1"}   
    r = get(url, headers=headers)
    print("writing to temp.mp4")
    with open("temp.mp4", 'wb+') as f:
        f.write(r.content)

    return([filename, duration_sec, out[4]])


def cut_video(videoparams):
    """Cuts downloaded video to ~30s"""
    filename = videoparams[0]
    duration_sec = videoparams[1]
    vid_url = videoparams[2]
    clip_length = 27
    mins = 300
    maxs = 900
    if duration_sec < 915:
        mins = 0
        maxs = duration_sec - clip_length - 30
    print("cutting a clip with ffmpeg")
    out = check_output(["ffmpeg", "-loglevel", "warning", "-y", "-ss", str(random.randint(mins, maxs)), "-i", "temp.mp4", "-t", str(clip_length), "-c", "copy", "-avoid_negative_ts", "make_zero", "vids/"+filename])

    filesize = os.path.getsize("vids/"+filename)

    print("wrote "+filename+", file size:", filesize)
    
    if filesize < 10000:
        print("very low filesize, something went wrong?")
        os.rename("vids/"+filename, "vids/bad/"+filename)
    else:
        values = (vid_url, title, filename, 0)
        c.execute("INSERT INTO uploads (url,title,filename,used) VALUES (?,?,?,?)", values)
        conn.commit()

# Main Loop
clips = 0
while clips < clip_amount:
    try:
        out = select_random()
        title = process_title(out[0].strip())
        duplicate_vid = c.execute('SELECT COUNT(*) FROM uploads WHERE title=?', (title,)).fetchone()[0]

        if title != "skip" and duplicate_vid == 0:
            videoparams = download_video(out)
            cut_video(videoparams)
            clips += 1
        
        else: 
            print("Skipping {}, already in uploads db or not a game".format(title))

    except (KeyboardInterrupt, SystemExit):
        raise
    except:
        print("Unexpected error:", sys.exc_info())
