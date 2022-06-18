import sqlite3


class Database:
    def __init__(self):
        self.conn = sqlite3.connect('users.db')
        self.cursor = self.conn.cursor()
        user = """
            CREATE TABLE IF NOT EXISTS users (key CHAR, user CHAR, email CHAR, phone CHAR, method CHAR, expire BIGINT)
        """
        stats = """
            CREATE TABLE IF NOT EXISTS stats (stat char, hits int, success int, failed int, errors int);
        """
        status = """
        CREATE TABLE IF NOT EXISTS status (ts, INTEGER, status CHAR, starttime CHAR, endtime CHAR, color CHAR, reasoning CHAR);
        """
        slack = """
            CREATE TABLE IF NOT EXISTS slack (user CHAR, webhook JSON, active INT);
        """

        self.cursor.execute(user)
        self.cursor.execute(stats)
        self.cursor.execute(status)
        self.cursor.execute(slack)
        self.conn.commit()

    def __del__(self):
        self.conn.commit()
