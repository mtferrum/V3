import logging

log = logging.getLogger('spyspace')


class QueryDictExecutor:

    def __init__(self, engineClass, *args, **kwargs):
        """
        Init sql engine with connection arguments
        Engine MUST have method:
          .execute(**kwargs)
        :param engineClass: (type) engine
        :param args: engine's args
        :param kwargs: engine's keyword args
        """
        assert hasattr(engineClass, 'execute')
        assert callable(engineClass.execute)
        self.engine = engineClass(*args, **kwargs)

    @staticmethod
    def pick_args_kwargs(args_len, kwargs_keys, *args, **kwargs):
        """
        Picked args and kwargs
        :param args_len: (int) number of picked args
        :param kwargs_keys: (list) keys of picked keyword args
        :param args: all args
        :param kwargs: all keyword args
        :return:
                picked_args: (list)
                picked_kwargs: (dict)
                remain_args: (list)
                remain_kwargs: (dict)
        """
        picked_args = ()
        remain_args = args
        picked_kwargs = {}
        remain_kwargs = kwargs
        if args_len:
            picked_args = tuple(args[i] for i in range(args_len) if len(args) >= i + 1)
            remain_args = tuple(args[i] for i in range(len(args)) if i > args_len - 1)
        if kwargs_keys:
            picked_kwargs = {key: kwargs[key] for key in kwargs_keys
                             if kwargs.get(key) is not None}
            remain_kwargs = {key: val for key, val in kwargs.items()
                             if key not in kwargs_keys}
        return picked_args, picked_kwargs, remain_args, remain_kwargs

    def get_format_positions(self, string):
        """
        Get args len and kwargs keys in string.format
        :param string: (str)
        :return:
                args_len: (int)
                kwargs_keys: (list)
        """
        start_i = 0
        format_attrs = []
        while True:
            start, stop = self.find_format_start_stop(string, start_i)
            start_i = stop + 1
            if stop != -1 and start != -1:
                format_attrs.append(string[start + 1:stop])
            else:
                args_len = format_attrs.count('')
                kwargs_keys = [attr for attr in format_attrs if attr != '']
                return args_len, kwargs_keys

    @staticmethod
    def find_format_start_stop(string, start):
        start = string.find('{', start)
        stop = -1
        if start >= 0:
            stop = string.find('}', start)
        return start, stop

    def execute_queries(self, queries_dict, *args, keys=None, **kwargs):
        """
        Executes queries from the dictionary
        :param queries_dict: dict contain the queries
        :param args: engine.execute args
        :param keys: keys for choice the execute queries in queries_dict
        :param kwargs: engine.execute keyword args
        :return: None
        """
        if not isinstance(queries_dict, dict):
            raise TypeError('"queries_dict" type did not "dict"')
        if not keys:
            keys = list(queries_dict.keys())

        for key in keys:
            query = queries_dict.get(key)
            if query:
                if not isinstance(query, str):
                    raise TypeError('"query" type did not "str"')
                log.debug('engine Executing query key: {}...'.format(key))
                self.engine.execute(query, *args, **kwargs)
                log.debug('engine Executed query key: {}'.format(key))
            else:
                log.warning('executor Not found key: {}'.format(key))

    def execute_query(self, queries_dict, key, *args, **kwargs):
        """
        Executes query from the dictionary by key
        :param queries_dict: dict contain the queries
        :param key: key for choice the execute query in queries_dict
        :param args: engine.execute and query.format args
        :param kwargs: engine.execute and query.format keyword args
        :return: list if select or None if other queries
        """
        if not isinstance(queries_dict, dict):
            raise TypeError('"queries_dict" type did not "dict"')
        query = queries_dict.get(key)

        if query:
            if not isinstance(query, str):
                raise TypeError('"query" type did not "str"')

            args_indexes, kwargs_keys = self.get_format_positions(query)
            a, k, args, kwargs = self.pick_args_kwargs(args_indexes, kwargs_keys,
                                                        *args, **kwargs)

            log.debug('engine Executing query key: {}...'.format(key))
            result = self.engine.execute(query.format(*a, **k), *args, **kwargs)
            log.debug('engine Executed query key: {}'.format(key))
        else:
            log.warning('executor Not found key: {}'.format(key))
            result = None
        return result
