import constants

import sqlite3


# This is a throwaway file used for one-off benchmarking and testing.

employees= 600
grants_per_employee_per_hour = 12
hours_per_day = 8
days_per_week = 5
weeks_per_year = 52
years = 5
total_grants = employees * grants_per_employee_per_hour * hours_per_day * days_per_week * weeks_per_year * years
# approx 75 million grants = 2.5GB of disk space

# employees= 400
# grants_per_employee_per_hour = 2
# hours_per_day = 8
# days_per_week = 5
# weeks_per_year = 48
# years = 5
# total_grants = employees * grants_per_employee_per_hour * hours_per_day * days_per_week * weeks_per_year * years
# approx 7.5 million grants = 0.25 GB of disk space

with sqlite3.connect(constants.DB_FILE_NAME) as conn:
    for i in range(total_grants):
        conn.execute("INSERT into grants (granter_id, recipient_id, amount) VALUES (1, 2, 1);")
    conn.commit()

    # conn.execute("DELETE FROM grants WHERE granter_id = 1 AND recipient_id = 2;")
    # conn.commit()
    #
    # cursor: sqlite3.Cursor = conn.execute('SELECT COUNT(*) AS total_grants FROM grants;')
    # results = cursor.fetchone()
    # print(results)
    #
    # # consolidate multiple DB files into 1
    # conn.execute('VACUUM;')
    # cursor: sqlite3.Cursor = conn.execute('PRAGMA wal_checkpoint(TRUNCATE);')
    # results: tuple[int, int, int] = cursor.fetchone()
    # if results[0]:
    #     raise SystemExit("truncation failed")
    # conn.commit()

    cursor: sqlite3.Cursor = conn.execute('SELECT COUNT(*) AS total_grants FROM grants;')
    results = cursor.fetchone()
    print(results)
