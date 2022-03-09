
import sqlite3


class Database:

    def __init__(self):
        self.conn = sqlite3.connect('users.db')
        self.cursor = self.conn.cursor()

        self.cursor.execute(
            'CREATE TABLE IF NOT EXISTS users (key CHAR, user CHAR, email CHAR, phone CHAR, method CHAR, expire BIGINT);'
        )
        self.cursor.execute(
            'CREATE TABLE IF NOT EXISTS stats (stat char, hits int, success int, failed int, errors int);'
        )
        self.cursor.execute(
            'CREATE TABLE IF NOT EXISTS status (status CHAR, starttime CHAR, endtime CHAR, color CHAR reasoning CHAR);'
        )

    def __del__(self):
        self.conn.commit()
