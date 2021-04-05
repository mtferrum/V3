from mysql.connector import MySQLConnection
import logging

log = logging.getLogger('spyspace')


class MySQLEngine(MySQLConnection):

    def __init__(self, host, connect_attempts=2, connect_delay=5, max_block_size=1000, **kwargs):
        """
        Engine for connection with the MySQL database.
        :param host: (str) host with running MySQL server.
        :param connect_attempts: (int) number of connection attempts
        :param connect_delay: (int) delay between connection attempts
        :param max_block_size: (int) delay between connection attempts
        :param kwargs: MySQLConnection keyword args
        """
        assert isinstance(host, str)
        assert isinstance(connect_attempts, int)
        assert isinstance(connect_delay, int)
        assert isinstance(max_block_size, int)
        super().__init__()
        self.config(host=host, **kwargs)
        self.connect_attempts = connect_attempts
        self.connect_delay = connect_delay
        self.max_block_size = max_block_size

    def execute(self, sql_query, *args, async_mode=False, many=False, commit=False, **kwargs):
        """
        Executes query.
        Establishes new connection if it wasn't established yet.

        :param sql_query: sql_query that will be send to database.
        :param args: cursor.execute or cursor.executemany args.
                    if many=True, INSERT can be `list` of `list` or `list` of `tuple`
        :param async_mode: (bool) True for using cursor.fetchmany
        :param many: (bool) True for using cursor.executemany
        :param commit: (bool) True for commit after execute
        :param kwargs: cursor.execute or cursor.executemany  keyword args
        :return: None for INSERT/CREATE etc queries or
                 `list` of `list` or `list` of `tuple` for SELECT queries
        e.g:
               engine.execute('insert into table (val1, val2) values (6, 9)')
               engine.execute('insert into table (val1, val2) values ('%s','%s')', [(1, 5), (3, 7)], many=True)
        """
        if not isinstance(sql_query, str):
            raise TypeError('"sql_query" type did not "str"')
        self.ping(reconnect=True, attempts=self.connect_attempts, delay=self.connect_delay)
        cursor = self.cursor()
        result = None
        log.debug('mysql Executing query: "{}"...'.format(sql_query.strip()))
        if many:
            cursor.executemany(sql_query, *args, **kwargs)
        else:
            cursor.execute(sql_query, *args, **kwargs)
        if self.unread_result:
            if async_mode:
                result = []
                rows = True
                while rows:
                    rows = cursor.fetchmany(self.max_block_size)
                    result.extend(rows)
            else:
                result = cursor.fetchall()
        if hasattr(result, '__len__'):
            log.debug('mysql Executed query with result len: {}'.format(len(result)))
        else:
            log.debug('mysql Executed query with result: {}'.format(result))

        if commit:
            self.commit()
            log.debug('mysql Commit query')
        cursor.close()
        return result

    def __del__(self):
        if hasattr(self, 'close'):
            self.close()
        log.debug('mysql Disconnected from host={}'.format(self.server_host))
        del self
