import redis
import bz2
import _pickle as pickle
import logging
import time

log = logging.getLogger('spyspace')


class RedisBus:
    """
    Args transport from pusher to subscribers via Redis
    """
    _subscribers = dict()

    def __init__(self, host='localhost', port=6379, db=0, queue_size=1024):
        self.client = redis.StrictRedis(host=host, port=port, db=db)
        self.queue_size = queue_size

    @staticmethod
    def _loads(payload):
        try:
            #return pickle.loads(bz2.decompress(payload), fix_imports=True, encoding="utf-8",
            #                    errors="strict")
            return pickle.loads(payload, fix_imports=True, encoding="utf-8",
                                errors="strict")
        except Exception as e:
            log.error('pickle loads error:' + str(e))
            return None

    @staticmethod
    def _dumps(data):
        try:
            return pickle.dumps(data, protocol=-1, fix_imports=True)
            #return bz2.compress(pickle.dumps(data, protocol=-1, fix_imports=True))
        except Exception as e:
            log.error('pickle dumps error:' + str(e))
            return None

    def _on_message(self, msg):
        args, kwargs = self._loads(msg)
        if self._subscribers.get(msg.topic):
            for fn in self._subscribers[msg.topic]:
                fn(*args, **kwargs)
        else:
            log.warning(
                'redis Callback _subscribers is not set for topic={}'.format(msg.topic))

    def subscribe(self, topic, fn=None):
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

        #while self.client.llen(topic) >= self.queue_size:
            #self.client.rpop(topic)

        send_data = self._dumps((args, kwargs))
        self.client.lpush(topic, send_data)

    def get_message(self, topic, stack=True):
        fns = self._subscribers.get(topic)
        if stack:
            msg = self.client.lpop(topic)
        else:
            msg = self.client.rpop(topic)
        if not msg:
            return None
        args, kwargs = self._loads(msg)
        for fn in fns:
            fn(*args, **kwargs)

    def get_messages(self, stack=True):
        for topic in self._subscribers.keys():
            self.get_message(topic, stack=stack)

    def listen(self, stack=True):
        while True:
            self.get_messages(stack=stack)
