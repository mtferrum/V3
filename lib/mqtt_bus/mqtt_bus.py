from paho.mqtt.client import Client
import pickle
import time
import logging


log = logging.getLogger()


class IBus:
    """
    Bus interface validator
    """
    def __init__(self):
        """
        Check attributes and methods required
        """
        # Attributes
        self._subscribers  # dict {(str) topic: (list of fn) subscribers}
        # Methods
        self.subscribe  # (self, topic, fn) Add function fn to topic subscribers list
        self.push  # (self, topic, *args, **kwargs) Call all the topic subscribers


class MqttBus(IBus):
    """
    Args transport from pusher to subscribers via MQTT
    """
    _subscribers = dict()

    def __init__(self, host=None, *args, publish_time_out=0.05, publish_waiting=0.1,
                 mid_max_len=64, qos=2, retain=True, **kwargs):
        super().__init__()
        if host is None:
            host = 'localhost'
        self.client = Client(*args, **kwargs)
        self.client.connect(host)
        self.client.loop_start()
        self.client.on_publish = self._on_publish
        self._received_messages = []
        self.mid_max_len = mid_max_len
        self.publish_time_out = publish_time_out
        self.publish_waiting = publish_waiting
        self.qos = qos
        self.retain = retain

    @staticmethod
    def _loads(payload):
        try:
            return pickle.loads(payload, fix_imports=True, encoding="utf-8",
                                errors="strict")
        except Exception as e:
            log.error('mqtt loads error:' + str(e))
            return None

    @staticmethod
    def _dumps(data):
        try:
            return pickle.dumps(data, protocol=3, fix_imports=True)
        except Exception as e:
            log.error('mqtt dumps error:' + str(e))
            return None

    def _on_publish(self, client, userdata, mid):
        if len(self._received_messages) >= self.mid_max_len:
            self._received_messages.pop(0)
            self._received_messages.append(mid)
        else:
            self._received_messages.append(mid)

    def _on_message(self, client, userdata, msg):

        args, kwargs = self._loads(msg.payload)
        if self._subscribers.get(msg.topic):
            for fn in self._subscribers[msg.topic]:
                fn(*args, **kwargs)
        else:
            log.warning(
                'mqtt Callback _subscribers is not set for topic={}'.format(msg.topic))

    def subscribe(self, topic, fn=None):
        """
        Add function fn to subscribers list
        """
        if fn:
            assert hasattr(fn, '__call__')
            self.client.subscribe(topic, qos=self.qos)
            self.client.message_callback_add(topic, lambda
                                             client, userdata, msg:
                                             self._on_message(client, userdata, msg))
            if self._subscribers.get(topic) is None:
                self._subscribers[topic] = [fn]
                log.info(
                    'mqtt Function {} subscribed to topic "{}"'.format(fn.__name__, topic))
            else:
                self._subscribers[topic].append(fn)
                log.info(
                    'mqtt Function {} subscribed to topic "{}"'.format(fn.__name__, topic))
        else:
            self.client.message_callback_remove(topic)
            self.client.unsubscribe(topic)

    def push(self, topic, *args, **kwargs):
        """
        Call all the subscribers
        """
        _args = [arg for arg in args if isinstance(arg, (float, int, str))]
        _kwargs = {key: arg for key, arg in kwargs.items() if isinstance(arg, (float, int, str))}

        if _args or _kwargs:
            log.debug('pushed topic "{}" with args {} and kwargs {} and {}'.format(
                topic, str(_args), str(_kwargs), str(set(kwargs.keys()) - set(_kwargs.keys()))))

        send_data = self._dumps((args, kwargs))
        log.info('mqtt Pushing data with size={} to topic={}...'.format(len(send_data), topic))
        rc, mid = self.client.publish(topic, send_data, qos=self.qos, retain=self.retain)
        publish_time = time.time()
        while mid not in self._received_messages:
            time.sleep(self.publish_time_out)
            if (time.time() - publish_time) >= self.publish_waiting:
                break
        if rc == 0:
            log.info('mqtt Pushed data to topic={} with rc {}'.format(topic, rc))
        else:
            log.warning('mqtt Not pushed data to topic={} with rc {}'.format(topic, rc))
