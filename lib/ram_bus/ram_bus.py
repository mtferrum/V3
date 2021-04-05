import logging


log = logging.getLogger()


class RamBus():
    """
    Args transport from pusher to subscribers via RAM
    """
    _subscribers = dict()
    _malfunction_subscribers = dict()

    def subscribe(self, topic, fn):
        """
        Add function fn to subscribers list
        """
        assert hasattr(fn, '__call__')

        if self._subscribers.get(topic) is None:
            self._subscribers[topic] = [fn]
            log.info('Function {} subscribed to topic "{}"'.format(fn.__name__, topic))
        else:
            self._subscribers[topic].append(fn)
            log.info('Function {} subscribed to topic "{}"'.format(fn.__name__, topic))

    def push(self, topic, *args, **kwargs):
        """
        Call all the subscribers
        """
        _args = [arg for arg in args if isinstance(arg, (float, int, str))]
        _kwargs = {key: arg for key, arg in kwargs.items() if isinstance(arg, (float, int, str))}
        if _args or _kwargs:
            log.debug('pushed topic "{}" with args {} and kwargs {} and {}'.format(
                topic, str(_args), str(_kwargs), str(set(kwargs.keys()) - set(_kwargs.keys()))))

        if self._subscribers.get(topic) is None:
            log.debug('No subscribers for topic "{}"'.format(topic))
            return

        str_subscribers = ', '.join([subscriber.__name__ for subscriber in self._subscribers[topic]])
        log.debug('Call subscribers: {}'.format(str_subscribers))

        for fn_pos, fn in enumerate(self._subscribers[topic]):
            try:
                fn(*args, **kwargs)
            except Exception as e:
                if self._malfunction_subscribers.get(fn.__name__) is None:
                    self._malfunction_subscribers[fn.__name__] = 1
                    log.exception(e)
                    log.error(
                        'Mafunction subscriber {} ({} errors) called by topic'
                        ' "{}" with args {} and kwargs {} and {}'.format(
                            fn.__name__,
                            self._malfunction_subscribers[fn.__name__],
                            topic,
                            str(_args),
                            str(_kwargs),
                            str(set(kwargs.keys()) - set(_kwargs.keys()))))
                elif self._malfunction_subscribers[fn.__name__] < 32:
                    self._malfunction_subscribers[fn.__name__] += 1
                    log.exception(e)
                    log.critical(
                        'Mafunction subscriber {} ({} errors) called by topic'
                        ' "{}" with args {} and kwargs {} and {}'.format(
                            fn.__name__,
                            self._malfunction_subscribers[fn.__name__],
                            topic,
                            str(_args),
                            str(_kwargs),
                            str(set(kwargs.keys()) - set(_kwargs.keys()))))
                else:
                    log.critical('MALFUNCTION SUBSCRIBER KILLED: {} (more than {} errors)'.format(fn.__name__, 32))
                    self._subscribers[topic].pop(fn_pos)

    def __del__(self):
        if self._malfunction_subscribers:
            log.critical("MALFUNCTION SUBSCRIBES FOUND: " + ", ".join([fn_name for fn_name in self._malfunction_subscribers.keys()]))
        del self
