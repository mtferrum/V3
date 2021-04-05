from scope import bus


class DataCollector:

    _data = dict()

    def __init__(self, subject, required_keys, fn):
        self.subject = subject
        self.required_keys = required_keys
        self.fn = fn
        self.bus = bus
        self.bus.subscribe(self.subject, self.add_data)

    def add_data(self, msg_id, **kwargs):
        """
        Append data got from pushers
        msg_id (str) message (row) id
        """
        if msg_id not in self._data:
            self._data[msg_id] = dict()
        for k, v in kwargs.items():
            self._data[msg_id][k] = v
        self.check_data_collected(msg_id)

    def check_data_collected(self, msg_id):
        """
        Check if all the keys are collected with data
        """
        if self.required_keys == set(self._data[msg_id].keys()):
            self.send_data(msg_id)

    def send_data(self, msg_id):
        """
        Call the self.fn function when all the data is collected
        """
        self.fn(*self._data[msg_id].values())
        self._data[msg_id] = dict()
