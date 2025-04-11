import sqlite3

src_conn = sqlite3.connect("bets.db")
dst_conn = sqlite3.connect("bet_sort.db")
src_cursor = src_conn.cursor()
dst_cursor = dst_conn.cursor()

dst_cursor.execute("PRAGMA foreign_keys = OFF;")

dst_cursor.execute("""
    CREATE TABLE bets (
        id INTEGER PRIMARY KEY,
        created_date TEXT,
        last_modified_date TEXT,
        heading TEXT,
        undertext TEXT,
        endtime TEXT,
        active TEXT,
        sort INTEGER,
        creator INTEGER,
        fix INTEGER,
        optionid INTEGER,
        countall INTEGER,
        tax_rate REAL
    );
""")

dst_cursor.execute("""
    CREATE TABLE bet_options (
        id INTEGER PRIMARY KEY,
        gameid INTEGER,
        created_date TEXT,
        last_modified_date TEXT,
        text TEXT,
        odds REAL,
        my_bonus REAL,
        bonus_total REAL,
        FOREIGN KEY (gameid) REFERENCES bets(id)
    );
""")

src_cursor.execute("SELECT * FROM bets ORDER BY id ASC;")
bets = src_cursor.fetchall()
dst_cursor.executemany("INSERT INTO bets VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", bets)

src_cursor.execute("SELECT * FROM bet_options ORDER BY id ASC;")
bet_options = src_cursor.fetchall()
dst_cursor.executemany("INSERT INTO bet_options VALUES (?, ?, ?, ?, ?, ?, ?, ?);", bet_options)

dst_cursor.execute("PRAGMA foreign_keys = ON;")

dst_conn.commit()
src_conn.close()
dst_conn.close()

