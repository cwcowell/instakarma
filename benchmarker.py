#!/usr/bin/env python3

from constants import *

import os
import sqlite3
import time


def init_db() -> None:
    try:
        os.remove(DB_FILE_NAME)
    except:
        pass
    with sqlite3.connect(DB_FILE_NAME) as conn:
        with open(DB_DDL_FILE_NAME) as ddl_file:
            ddl: str = ddl_file.read()
        conn.executescript(ddl)
        conn.commit()


def add_entity(conn: sqlite3.Connection, i_as_str: str) -> None:
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
    with sqlite3.connect(DB_FILE_NAME) as conn:
        while time.perf_counter() - start < 1.0:
            add_entity(conn, str(i))
            i += 1

        conn.commit()

        cursor: sqlite3.Cursor = conn.execute("SELECT COUNT(*) FROM entities;")
        print(f"total rows: {cursor.fetchone()[0]}")
