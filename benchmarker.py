#!/usr/bin/env python3

from constants import *

import os
import sqlite3
import time

def init_db() -> None:
    try:
        os.remove(DB_FILE)
    except:
        pass
    with sqlite3.connect(DB_FILE) as conn:
        with open(DB_DDL_FILE) as ddl_file:
            ddl: str = ddl_file.read()
        conn.executescript(ddl)
        conn.commit()

def add_entity(i_as_str: str) -> None:
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("""
                     INSERT INTO entities (name, user_id)
                     VALUES (?, ?)
                     """,
                     (i_as_str, i_as_str))
        conn.commit()

if __name__ == "__main__":
    init_db()
    i: int = 0
    start = time.perf_counter()
    while time.perf_counter() - start < 30.0:
        i_as_str: str = str(i)
        add_entity(i_as_str)
        i += 1

    with sqlite3.connect(DB_FILE) as conn:
        cursor: sqlite3.Cursor = conn.execute("SELECT COUNT(*) FROM entities;")
        print(f"total rows: {cursor.fetchone()[0]}")
