import sqlite3
conn = sqlite3.connect("playlist.db")
c = conn.cursor()
table_string = f"""CREATE TABLE IF NOT EXISTS uploads (
                url TEXT NOT NULL UNIQUE,
                title TEXT NOT NULL,
                filename TEXT NOT NULL,
                used INT NOT NULL,
                time TIMESTAMP DEFAULT CURRENT_TIMESTAMP);"""

c.execute(table_string)