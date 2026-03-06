import sqlite3
import shelve

shelf_db_path = "data/economy"
sqlite_db_path = "database.db"

shelf = shelve.open(shelf_db_path)
sqlite_conn = sqlite3.connect(sqlite_db_path)
cursor = sqlite_conn.cursor()

# TABLES
cursor.execute('''
CREATE TABLE IF NOT EXISTS users_balance (
    user_id INTEGER PRIMARY KEY,
    balance INTEGER NOT NULL DEFAULT 0,
    last_claimed DATE,
    total_claimed INTEGER NOT NULL DEFAULT 0,
    streak INTEGER NOT NULL DEFAULT 0,
    highest_streak INTEGER NOT NULL DEFAULT 0
)
''')

try:
    for key in shelf.keys():
        print(f"{key}: {shelf[key]}", end=",")

        cursor.execute("""
        INSERT OR REPLACE INTO users_balance (user_id, balance, last_claimed, total_claimed, streak) VALUES (?, ?, ?, ?, ?)""",
        (key, shelf[key]['balance'], shelf[key]['daily']['last_claimed'], shelf[key]['daily']['total_claimed'], shelf[key]['daily']['streak'])
        )

    sqlite_conn.commit()

except Exception as e:
    print(f"An error occurred: {e}")
    sqlite_conn.rollback()


shelf.close()
sqlite_conn.close()
