import sqlite3
import logging
import os

logging.basicConfig(level=logging.INFO)

class Database():

    def __init__(self):
        db_directory = os.path.join(os.path.dirname(__file__), '../db')
        os.makedirs(db_directory, exist_ok=True)
        self.connection = sqlite3.connect(os.path.join(db_directory, 'malware.db'))
        self.cursor = self.connection.cursor()

    def create_table(self) -> None:
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS malware (
                                timestamp TEXT,
                                filename TEXT,
                                hash TEXT UNIQUE,
                                ip TEXT
                            )''')
        self.connection.commit()

    def insert_data(self, timestamp, filename, hash, ip) -> None:
        try:
            self.cursor.execute('''INSERT INTO malware (timestamp, filename, hash, ip)
                                    VALUES (?, ?, ?, ?)''', (timestamp, filename, hash, ip))
            self.connection.commit()
        except sqlite3.IntegrityError:
            logging.exception("IntegrityError: Duplicate hash entry.")

    def truncate_table(self) -> None:
        self.cursor.execute('DELETE FROM malware')
        self.connection.commit()
        self.cursor.execute('VACUUM')
        self.connection.commit()

    def list_entries(self) -> None:
        self.cursor.execute('SELECT * FROM malware')
        rows = self.cursor.fetchall()
        for row in rows:
            print(row)

    def close(self) -> None:
        self.connection.close()

        