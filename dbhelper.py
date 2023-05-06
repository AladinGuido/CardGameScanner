import sqlite3


class DBHelper:

    def __init__(self, db_path):
        self.db_path = db_path
        self.db_connection = sqlite3.connect(db_path)
        self.cursor = self.db_connection.cursor()

    def query(self, query):
        self.cursor.execute(query)
        results = self.cursor.fetchall()

        return results
