import sqlite3

class Database:
    # Because this class is used in multiple cogs, a singleton is needed
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.DB_NAME = "database.db"
        self.conn = sqlite3.connect(self.DB_NAME, check_same_thread=False)
        self.cursor = self.conn.cursor()

        self.cursor.execute("PRAGMA foreign_keys = ON")

        self._init_db()
        self._initialized = True

    def close(self):
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.conn.commit()
        else:
            self.conn.rollback()

    ################## INITIALIZE DB ################

    def _init_db(self):
        """Creates the tables if needed."""
        with self.conn:
            self.cursor.execute("PRAGMA foreign_keys = ON")
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS whitelist (
                    user_id INTEGER PRIMARY KEY
                )
            ''')
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS projects (
                    guild_id INTEGER PRIMARY KEY,
                    project_name TEXT NOT NULL
                )
            ''')
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task TEXT NOT NULL,
                    guild_id INTEGER,
                    deadline DATE,
                    FOREIGN KEY (guild_id) REFERENCES projects (guild_id)
                )
            ''')
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS assign (
                    id INTEGER,
                    assigned_to TEXT,
                    PRIMARY KEY (id, assigned_to),
                    FOREIGN KEY (id) REFERENCES tasks (id)
                )
            ''')
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS finished (
                    id INTEGER PRIMARY KEY,
                    finished_by TEXT,
                    date_finished DATE,
                    FOREIGN KEY (id) REFERENCES tasks (id)
                )
            ''')
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS users_balance (
                    user_id INTEGER PRIMARY KEY,
                    balance INTEGER NOT NULL DEFAULT 0,
                    last_claimed DATE,
                    total_claimed INTEGER NOT NULL DEFAULT 0,
                    streak INTEGER NOT NULL DEFAULT 0,
                    highest_streak INTEGER NOT NULL DEFAULT 0
                )
            ''')

    ################## WHITELIST METHODS ##################

    def add_to_whitelist(self, user_id):
        self.cursor.execute('INSERT OR IGNORE INTO whitelist (user_id) VALUES (?)', (user_id,))
        return self.cursor.rowcount > 0

    def remove_from_whitelist(self, user_id):
        self.cursor.execute('DELETE FROM whitelist WHERE user_id = ?', (user_id,))
        return self.cursor.rowcount > 0

    def is_whitelisted(self, user_id):
        self.cursor.execute('SELECT 1 FROM whitelist WHERE user_id = ?', (user_id,))
        return self.cursor.fetchone() is not None

    ############# TASK TRACKER METHODS #############

    def guild_entry(self, guild_id, guild_name):
        self.cursor.execute('INSERT OR IGNORE INTO projects (guild_id, project_name) VALUES (?, ?)', (guild_id, guild_name))

    def add_task(self, guild_id, date, title):
        self.cursor.execute('INSERT INTO tasks (guild_id, deadline, task) VALUES (?, ?, ?)', (guild_id, date, title))
        self.cursor.execute('SELECT id FROM tasks WHERE guild_id = ? ORDER BY id DESC LIMIT 1', (guild_id,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def assign_task(self, task_id, assigned_to):
        self.cursor.execute('INSERT INTO assign (id, assigned_to) VALUES (?, ?)', (task_id, assigned_to))
        return self.cursor.rowcount > 0

    def id_exists(self, task_id):
        self.cursor.execute('SELECT 1 FROM tasks WHERE id = ?', (task_id,))
        return self.cursor.fetchone() is not None

    def guild_id_match_task(self, task_id, guild_id):
        self.cursor.execute('SELECT 1 FROM tasks WHERE id = ? AND guild_id = ?', (task_id, guild_id))
        return self.cursor.fetchone() is not None

    def finish_task(self, task_id, finished_by, date_finished):
        self.cursor.execute('INSERT INTO finished (id, finished_by, date_finished) VALUES (?, ?, ?)', (task_id, finished_by, date_finished))

    def project_exists(self, guild_id):
        self.cursor.execute('SELECT 1 FROM projects WHERE guild_id = ?', (guild_id,))
        return self.cursor.fetchone() is not None

    def get_all_tasks(self, guild_id):
        self.cursor.execute('''
            SELECT t.id, t.task, t.deadline, GROUP_CONCAT(a.assigned_to, ', ')
            FROM tasks t
            LEFT JOIN assign a ON t.id = a.id
            WHERE t.guild_id = ?
            GROUP BY t.id
        ''', (guild_id,))
        return self.cursor.fetchall()

    def get_in_progress_tasks(self, guild_id):
        self.cursor.execute('''
            SELECT t.id, t.task, t.deadline, GROUP_CONCAT(a.assigned_to, ', ')
            FROM tasks t
            LEFT JOIN assign a ON t.id = a.id
            LEFT JOIN finished f ON t.id = f.id
            WHERE t.guild_id = ? AND f.id IS NULL
            GROUP BY t.id
        ''', (guild_id,))
        return self.cursor.fetchall()

    def get_tasks_by_user(self, guild_id, user_id):
        self.cursor.execute('''
            SELECT t.id, t.task, t.deadline, GROUP_CONCAT(a.assigned_to, ', ')
            FROM tasks t
            JOIN assign a ON t.id = a.id
            LEFT JOIN finished f ON t.id = f.id
            WHERE f.id IS NULL AND (t.id) IN (
                SELECT t.id
                FROM tasks t
                JOIN assign a ON t.id = a.id
                WHERE t.guild_id = ? AND a.assigned_to = ?)
            GROUP BY t.id
        ''', (guild_id, user_id))
        return self.cursor.fetchall()

    def change_task_name(self, task_id, new_task_name):
        self.cursor.execute('UPDATE tasks SET task = ? WHERE id = ?', (new_task_name, task_id))
        return self.cursor.rowcount > 0

    def change_task_deadline(self, task_id, new_deadline):
        self.cursor.execute('UPDATE tasks SET deadline = ? WHERE id = ?', (new_deadline, task_id))
        return self.cursor.rowcount > 0

    def remove_assigned_user(self, task_id, assigned_to):
        self.cursor.execute('DELETE FROM assign WHERE id = ? AND assigned_to = ?', (task_id, assigned_to))
        return self.cursor.rowcount > 0

    def change_project_name(self, guild_id, new_name):
        self.cursor.execute('UPDATE projects SET project_name = ? WHERE guild_id = ?', (new_name, guild_id))
        return self.cursor.rowcount > 0

    ########################### MONEY RELATED METHODS ###########################

    def add_user_balance(self, user_id):
        self.cursor.execute('INSERT OR IGNORE INTO users_balance (user_id) VALUES (?)', (user_id,))

    def get_last_claimed(self, user_id):
        self.cursor.execute('SELECT last_claimed FROM users_balance WHERE user_id = ?', (user_id,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def add_streak(self, user_id):
        self.cursor.execute('UPDATE users_balance SET streak = streak + 1 WHERE user_id = ?', (user_id,))
        self.cursor.execute('''
            UPDATE users_balance
            SET highest_streak = CASE
                WHEN streak > highest_streak THEN streak
                ELSE highest_streak
            END
            WHERE user_id = ?
        ''', (user_id,))

    def reset_streak(self, user_id):
        self.cursor.execute('UPDATE users_balance SET streak = 1 WHERE user_id = ?', (user_id,)) # 1 bc is claiming

    def daily_claim(self, user_id, amount, last_claimed):
        self.cursor.execute('UPDATE users_balance SET balance = balance + ?, last_claimed = ?, total_claimed = total_claimed + 1 WHERE user_id = ?', (amount, last_claimed, user_id))

    def get_streak(self, user_id):
        self.cursor.execute('SELECT streak FROM users_balance WHERE user_id = ?', (user_id,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def get_balance(self, user_id):
        self.cursor.execute('SELECT balance FROM users_balance WHERE user_id = ?', (user_id,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def update_balance(self, user_id, amount):
        self.cursor.execute('UPDATE users_balance SET balance = balance + ? WHERE user_id = ?', (amount, user_id))

db = Database()