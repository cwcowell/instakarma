# #!/usr/bin/env python3
#
# from constants import *
#
# import os
# import sqlite3
# import time
#
#
# def init_db() -> None:
#     try:
#         os.remove(DB_FILE_NAME)
#     except:
#         pass
#     with sqlite3.connect(DB_FILE_NAME) as conn:
#         with open(DB_DDL_FILE_NAME) as ddl_file:
#             ddl: str = ddl_file.read()
#         conn.executescript(ddl)
#         conn.commit()
#
#
# def add_entity(conn: sqlite3.Connection, i_as_str: str) -> None:
#     conn.execute("""
#                  INSERT INTO entities (name, user_id)
#                  VALUES (?, ?)
#                  """,
#                  (i_as_str, i_as_str))
#     conn.commit()
#
#
# if __name__ == "__main__":
#     init_db()
#     i: int = 0
#     start = time.perf_counter()
#     with sqlite3.connect(DB_FILE_NAME) as conn:
#         while time.perf_counter() - start < 1.0:
#             add_entity(conn, str(i))
#             i += 1
#
#         conn.commit()
#
#         cursor: sqlite3.Cursor = conn.execute("SELECT COUNT(*) FROM entities;")
#         print(f"total rows: {cursor.fetchone()[0]}")


import sqlite3
import time

def setup_test_database():
    """Create a test database with sample data"""
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()

    # Create a test table
    cursor.execute('''
        CREATE TABLE test_table (
            id INTEGER PRIMARY KEY,
            value INTEGER
        )
    ''')

    # Insert 1000 rows with random values (some zero, some non-zero)
    from random import randint
    data = [(i, randint(0, 10)) for i in range(10000000)]
    cursor.executemany('INSERT INTO test_table (id, value) VALUES (?, ?)', data)
    conn.commit()

    return conn

def method1_filter_in_db():
    """Filter non-zero values using SQL"""
    conn = setup_test_database()
    cursor = conn.cursor()

    start_time = time.perf_counter()

    # Let the database do the filtering
    cursor.execute('SELECT * FROM test_table WHERE value != 0')
    results = cursor.fetchall()

    end_time = time.perf_counter()
    conn.close()

    return len(results), end_time - start_time

def method2_filter_in_python():
    """Filter non-zero values in Python"""
    conn = setup_test_database()
    cursor = conn.cursor()

    start_time = time.perf_counter()

    # Get all rows and filter in Python
    cursor.execute('SELECT * FROM test_table')
    all_results = cursor.fetchall()
    results = [row for row in all_results if row[1] != 0]

    end_time = time.perf_counter()
    conn.close()

    return len(results), end_time - start_time

# Run the comparison
db_count, db_time = method1_filter_in_db()
py_count, py_time = method2_filter_in_python()

print(f"Database filtering: {db_count} rows in {db_time:.6f} seconds")
print(f"Python filtering:   {py_count} rows in {py_time:.6f} seconds")
print(f"Ratio: Python is {py_time/db_time:.2f}x slower")