import sqlite3
import datetime


class Stats:

    def __init__(self):
        self.connect = sqlite3.connect('users.db')
        self.cursor = self.connect.cursor()

    async def unauthorized(self):
        ''' Increases the Failed ticker by one.'''
        self.cursor.execute(
            'UPDATE stats SET failed = failed + 1 WHERE stat = stat;'
            )
        self.connect.commit()

    async def hits(self):
        ''' Increases hit counter by one.'''
        self.cursor.execute(
            'UPDATE stats SET hits = hits +1 WHERE stat = stat;'
        )
        self.connect.commit()

    async def authorized(self):
        ''' Increases the success counter by 1'''
        self.cursor.execute(
            'UPDATE stats SET success = success + 1 WHERE stat = stat;'
        )

    async def errors(self):
        ''' Increases the error counter'''
        self.cursor.execute(
            'UPDATE stats SET errors = errors +1 WHERE stat = stat;'
        )
        self.connect.commit()

    async def changestatus(self, color=None, reason=None):
        ''' Registers a status change in the database.'''
        now = datetime.datetime.now()
        data = self.cursor.execute(
            'SELECT status FROM status WHERE status == "ongoing";'
        ).fetchone()
        if len(data) > 0:
            self.cursor.execute(
                f'UPDATE status SET (status, endtime) VALUES("ended", "{now}") WHERE status == "ongoing";'
            )
        else:
            self.cursor.execute(
                f'INSERT INTO status ("ongoing", "{now}", "null", "{color}", "{reason}");'
            )
        self.connect.commit()

    async def get_stats(self):
        ''' Returns raw database data from stats table'''

        sql = 'SELECT * FROM stats WHERE stat = "stat";'
        return self.cursor.execute(sql).fetchone()
