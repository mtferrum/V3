from query_executor import QueryDictExecutor


def assertRaises(exception, method, *args, **kwargs):
    try:
        method(*args, **kwargs)
    except exception:
        return True
    else:
        raise AssertionError('method does not raise exception {}'.format(exception))


class MockEngine:
    """
    Mock class for Engine
    """

    def execute(self, query):
        res = 'MockEngine successful {} result'.format(query)
        return res


class EmptyMockEngine:
    """
    Mock class for Engine with no methods
    """


class UncallableMockEngine:
    """
    Mock class for Engine with no methods but with execute attr
    """
    execute = True


mock_input = {'test1': 'query1', 'test2': 'query2'}
not_str_in_dict_mock_input = {'test1': 1, 'test2': True}
not_dict_mock_input = 1
mock_keys = ['test1', 'test2']
empty_list_mock_keys = []
not_list_mock_keys = True
mock_key = 'test1'

executor = QueryDictExecutor(MockEngine)
assert isinstance(executor.engine, MockEngine)
assertRaises(AssertionError, QueryDictExecutor, EmptyMockEngine)
assertRaises(AssertionError, QueryDictExecutor, UncallableMockEngine)

executor.execute_queries(mock_input)
assertRaises(TypeError, QueryDictExecutor.execute_queries, not_dict_mock_input)
assertRaises(TypeError, QueryDictExecutor.execute_queries, not_str_in_dict_mock_input)

executor.execute_queries(mock_input, keys=mock_keys)
executor.execute_queries(mock_input, keys=empty_list_mock_keys)
assertRaises(TypeError, QueryDictExecutor.execute_queries, mock_input,
             keys=not_list_mock_keys)

executor.execute_query(mock_input, mock_key)
assertRaises(TypeError, QueryDictExecutor.execute_query, mock_input)
