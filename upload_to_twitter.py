# Uploads processed video clips to twitter

import sqlite3
import twitter
from secrets import *
import sys
import os

filepath = os.path.dirname(os.path.realpath(sys.argv[0]))

conn = sqlite3.connect(filepath+"/playlist.db")
c = conn.cursor()
d = c.execute('SELECT * FROM uploads WHERE used=0 LIMIT 1').fetchone()
title = d[1]
filename = d[2]
print(title, filename)

c.execute('UPDATE uploads SET used=1 WHERE title=?', (title,))
conn.commit()

api = twitter.Api(consumer_key=consumer_key,
                  consumer_secret=consumer_secret,
                  access_token_key=access_token,
                  access_token_secret=access_secret)


status = api.PostUpdate(title, media=filepath+"/vids/"+filename)