
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

    def get_snippets(self):
        with self.connect() as connection:
            cursor = connection.execute("""
                SELECT id, title, category, code
                FROM snippets
                ORDER BY title COLLATE NOCASE
            """)
            return cursor.fetchall()

    def add_snippet(self, title, category, code):
        with self.connect() as connection:
            cursor = connection.execute("""
                INSERT INTO snippets (title, category, code)
                VALUES (?, ?, ?)
            """, (title, category, code))
            return cursor.lastrowid

    def update_snippet(self, snippet_id, title, category, code):
        with self.connect() as connection:
            connection.execute("""
                UPDATE snippets
                SET title = ?, category = ?, code = ?
                WHERE id = ?
            """, (title, category, code, snippet_id))

    def delete_snippet(self, snippet_id):
        with self.connect() as connection:
            connection.execute("""
                DELETE FROM snippets
                WHERE id = ?
            """, (snippet_id,))

    def add_test_case(self, problem, input_data, expected_output):
        with self.connect() as connection:
            cursor = connection.execute("""
                INSERT INTO test_cases (problem, input, output)
                VALUES (?, ?, ?)
            """, (problem, input_data, expected_output))

            return cursor.lastrowid


    def get_test_cases(self):
        with self.connect() as connection:
            cursor = connection.execute("""
                SELECT id, problem, input, output
                FROM test_cases
                ORDER BY id DESC
            """)

            return cursor.fetchall()


    def get_test_cases_by_problem(self, problem):
        with self.connect() as connection:
            cursor = connection.execute("""
                SELECT id, problem, input, output
                FROM test_cases
                WHERE problem = ?
                ORDER BY id DESC
            """, (problem,))

            return cursor.fetchall()

    def update_test_case(self, test_id, problem, input_data, expected_output):
        with self.connect() as connection:
            connection.execute("""
                UPDATE test_cases
                SET problem = ?, input = ?, output = ?
                WHERE id = ?
            """, (problem, input_data, expected_output, test_id))


    def delete_test_case(self, test_id):
        with self.connect() as connection:
            connection.execute("""
                DELETE FROM test_cases
                WHERE id = ?
            """, (test_id,))
