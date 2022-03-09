
from typing import Any


class Users:

    def __init__(self, db):
        self.cursor = db.cursor
        self.user = None

    def sql(self, key) -> Any:
        
        """ Requests the user data from the database"""
        sql = 'SELECT * FROM users WHERE key = ?'
        data = self.cursor.execute(sql, [key, ])
        return data.fetchall()

    def check(self, key) -> bool:
        ''' Checks if key is in database'''

        data = self.sql(key)
        if data and len(data) == 1:
            self.user = data[0]
            return True
        elif data and len(data) > 1:
            print(f'Error, too many results for this api key:{key}')
            return False
        return False

    def add(self, **user) -> None:
        pass
