from _datetime import datetime
import uuid


class Ping:

    def __init__(self, bus, period=300):
        self.bus = bus
        self.iterations = {}
        self.send_period = period
        self.msg_id = None
        self.bus.subscribe('msg_id', self._msg_id_update)

    def _msg_id_update(self, msg_id):
        self.msg_id = msg_id

    def _get_msg(self, topic):
        if hasattr(self.bus, 'get_messages'):
            if callable(self.bus.get_message):
                self.bus.get_message(topic, stack=False)

    def ping_stage(self, name, start=False, final=False):
        if self.iterations.get(name) is None:
            self.iterations[name] = 0
        self.iterations[name] += 1
        if self.iterations[name] >= self.send_period:
            self.iterations[name] = 0
            ts = datetime.now()
            kw = {name: ts}
            if self.msg_id is None:
                if start:
                    self.msg_id = uuid.uuid4()
                    self.bus.push('msg_id', self.msg_id)
                else:
                    self._get_msg('msg_id')
                    self.bus.push('msg_id', self.msg_id)
            self.bus.push('ping', self.msg_id, **kw)
            if final:
                self._get_msg('msg_id')
                self.msg_id = None
                self._get_msg('ping')
