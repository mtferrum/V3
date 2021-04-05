from mysql_engine import MySQLEngine


def assertRaises(exception, method, *args, **kwargs):
    try:
        method(*args, **kwargs)
    except exception:
        return True
    else:
        raise AssertionError('method does not raise exception {}'.format(exception))


mock_database = '127.0.0.1'
not_str_mock_database = 1337

mock_query = 'select * from test'
not_str_mock_query = 1984

engine = MySQLEngine(mock_database)
assertRaises(AssertionError, MySQLEngine, not_str_mock_database)

assertRaises(AssertionError, engine.execute, mock_query)
assertRaises(TypeError, MySQLEngine.execute, not_str_mock_query)
