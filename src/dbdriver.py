import sqlite3 as sl

class DBDriver:
    def __init__(self, db):
        self.conn = sl.connect(db)
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS user (
                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    username TEXT,
                    name TEXT,
                    password TEXT
                );
            """)

    def insert_row(self, table, data: dict):
        columns = []
        values = []
        for k, v in data.items():
            columns.append(k)
            values.append(v)

        query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join(['?'] * len(data))}"
        with self.conn:
            self.conn.execute(query, values)

    def get_columns(self, table: str, columns: list[str]):
        data = {}
        for column in columns:
            data[column] = []

        with self.conn:
            data = self.conn.execute(f"SELECT {', '.join(columns)} FROM {table}").fetchall()

        return data

