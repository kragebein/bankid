import sqlite3
import time

# from bankid.slack import Slack
import datetime


class Stats:
    def __init__(self, db: sqlite3.Connection):
        self.db = db
        self.connect = db.conn
        self.cursor = db.cursor
        # self.slack = Slack()

    async def unauthorized(self):
        '''Increases the Failed ticker by one.'''
        self.cursor.execute('UPDATE stats SET failed = failed + 1 WHERE stat = stat;')
        await self.hits()
        self.connect.commit()

    async def hits(self):
        '''Increases hit counter by one.'''
        self.cursor.execute('UPDATE stats SET hits = hits +1 WHERE stat = stat;')

    async def authorized(self):
        '''Increases the success counter by 1'''
        self.cursor.execute('UPDATE stats SET success = success + 1 WHERE stat = stat;')
        await self.hits()
        self.connect.commit()

    async def errors(self):
        '''Increases the error counter'''
        self.cursor.execute('UPDATE stats SET errors = errors +1 WHERE stat = stat;')
        await self.hits()
        self.connect.commit()

    async def changestatus(self, color=None, reason=None):
        '''Registers a status change'''

        # colors = {
        #    'yellow': ':large_yellow_circle:',
        #    'green': ':large_green_circle:',
        #    'red': ':red_circle:',
        #    'orange': ':large_orange_circle',
        #    'black': ':black_circle',
        #    'grey': ':white_circle',
        # }

        now = int(time.time())
        data = self.cursor.execute('SELECT color FROM status WHERE status = ?;', ('ongoing',)).fetchone()

        # if color != data[0]:
        #    self.slack.send(
        #        ['#bankid'],
        #        change=f'{colors[data[0]]} :arrow_right: {colors[color]}',
        #        reason=reason
        #    )

        if data and color != data[0]:

            self.cursor.execute("UPDATE status SET status = ?, endtime = ? WHERE status = ?;", ('ended', now, 'ongoing'))

        elif color == data[0]:
            return
        else:

            self.cursor.execute(
                'INSERT INTO status (status, starttime, endtime, color, reasoning) VALUES(?, ?, ?, ?, ?);',
                ('ongoing', now, 'null', color, reason),
            )

        self.connect.commit()

    async def get_stats(self):
        '''Returns raw database data from stats table'''

        sql = 'SELECT * FROM stats WHERE stat = "stat";'
        return self.cursor.execute(sql).fetchone()


class Timeline:
    '''Asyncio worker that keeps track of the last 186 hours for historic timeline'''

    def __init__(self):
        self.conn = sqlite3.connect('status.db')
        self.cursor = self.conn.cursor()

    def put(self, status, color):
        query = 'INSERT INTO status (status, color) VALUES(?, ?);'
        self.cursor.execute(query, (status, color))
        self.conn.commit()

    def e2t(self, n: int) -> datetime:
        return datetime.datetime.fromtimestamp(n).strftime('%Y-%m-%d %H:59:59')

    def query(self):
        now = int(self.cursor.execute("SELECT strftime('%s', 'now') as INT").fetchone()[0])
        first = now - 604800

        start = first
        end = start + 3600
        c = 0

        query = """
            SELECT
                time, status, color
            FROM
                status
            WHERE
                time
            BETWEEN
                ?
            AND
                ?
        """

        for _ in range(first, now, 3600):
            # Inside the hour.

            results = self.cursor.execute(query, (start, end)).fetchall()
            dict_results = {'red': [], 'orange': [], 'yellow': [], 'green': [], 'blue': [], 'black': []}
            for x in reversed(results):
                _time, status, color = x
                dict_results[color] = status, _time

            for k, v in dict_results.items():
                if k == 'red' and len(v) > 0:
                    yield {'time': str(self.e2t(v[1])), 'color': k, 'status': v[0]}
                    break
                elif k == 'orange' and len(v) > 0:
                    yield {'time': str(self.e2t(v[1])), 'color': k, 'status': v[0]}
                    break
                elif k == 'blue' and len(v) > 0:
                    yield {'time': str(self.e2t(v[1])), 'color': k, 'status': v[0]}
                    break
                elif k == 'green' and len(v) > 0:
                    yield {'time': str(self.e2t(v[1])), 'color': k, 'status': v[0]}
                    break
                elif k == 'grey' and len(v) > 0:
                    yield {'time': str(self.e2t(v[1])), 'color': k, 'status': v[0]}
                    break
                elif k == 'black' and len(v) > 0:
                    yield {'time': str(self.e2t(v[1])), 'color': k, 'status': v[0]}
                    break

            start += 3600
            end += 3600
            c += 1


if __name__ == "__main__":
    _test = Timeline()
    for _testy in _test.query():
        print(_testy)
