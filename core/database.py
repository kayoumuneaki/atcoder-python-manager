import sqlite3


class Database:
    def __init__(self, db_path="database.db"):
        self.db_path = db_path

    def connect(self):
        return sqlite3.connect(self.db_path)

    def initialize(self):
        with self.connect() as connection:
            self.create_settings_table(connection)
            self.create_snippets_table(connection)
            self.create_test_cases_table(connection)

    def create_settings_table(self, connection):
        connection.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)

    def create_snippets_table(self, connection):
        connection.execute("""
            CREATE TABLE IF NOT EXISTS snippets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                category TEXT,
                code TEXT NOT NULL
            )
        """)

    def create_test_cases_table(self, connection):
        connection.execute("""
            CREATE TABLE IF NOT EXISTS test_cases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                problem TEXT NOT NULL,
                input TEXT,
                output TEXT
            )
        """)