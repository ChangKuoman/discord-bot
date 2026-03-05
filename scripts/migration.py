import sqlite3
import shelve

shelf_db_path = "data/tasks"
sqlite_db_path = "database.db"

shelf = shelve.open(shelf_db_path)
sqlite_conn = sqlite3.connect(sqlite_db_path)
cursor = sqlite_conn.cursor()

# TABLES
cursor.execute('''
CREATE TABLE IF NOT EXISTS projects (
    guild_id INTEGER PRIMARY KEY,
    project_name TEXT NOT NULL
)
''')
cursor.execute('''
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task TEXT NOT NULL,
    guild_id INTEGER,
    deadline DATE,
    FOREIGN KEY (guild_id) REFERENCES projects (guild_id)
)
''')
cursor.execute('''
CREATE TABLE IF NOT EXISTS assign (
    id INTEGER,
    assigned_to TEXT,
    PRIMARY KEY (id, assigned_to),
    FOREIGN KEY (id) REFERENCES tasks (id)
)
''')
cursor.execute('''
CREATE TABLE IF NOT EXISTS finished (
    id INTEGER PRIMARY KEY,
    finished_by TEXT,
    date_finished DATE,
    FOREIGN KEY (id) REFERENCES tasks (id)
)
''')

try:
    for key in shelf.keys():
        print(f"{key}: {shelf[key]}", end=",")

        cursor.execute("""
        INSERT OR REPLACE INTO projects (guild_id, project_name) VALUES (?, ?)""", (key, shelf[key]['title']
        ))
        for task_id, task_info in shelf[key]['tasks'].items():
            cursor.execute("""
            INSERT INTO tasks (id, task, guild_id, deadline) VALUES (?, ?, ?, ?)""",
            (task_id, task_info['title'], key, task_info['deadline'])
            )

            assigned_to = task_info['assigned_to']
            if assigned_to:
                cursor.execute("""
                INSERT INTO assign (id, assigned_to) VALUES (?, ?)""",
                (task_id, assigned_to)
                )

            if task_info['status'] == 'finished':
                finished_by = task_info['finished_by']
                date_finished = task_info['finished_on']
                cursor.execute("""
                INSERT INTO finished (id, finished_by, date_finished) VALUES (?, ?, ?)""",
                (task_id, finished_by, date_finished)
                )

    sqlite_conn.commit()

except Exception as e:
    print(f"An error occurred: {e}")
    sqlite_conn.rollback()


shelf.close()
sqlite_conn.close()
