import sqlite3

DB_NAME = "database.db"

def init_db():

    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS whitelist (
                user_id INTEGER PRIMARY KEY
            )
        ''')
        conn.commit()

def add_to_whitelist(user_id):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT OR IGNORE INTO whitelist (user_id) VALUES (?)', (user_id,))
        conn.commit()

        return cursor.rowcount > 0

def remove_from_whitelist(user_id):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM whitelist WHERE user_id = ?', (user_id,))
        conn.commit()

        return cursor.rowcount > 0

def is_whitelisted(user_id):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT 1 FROM whitelist WHERE user_id = ?', (user_id,))
        return cursor.fetchone() is not None
