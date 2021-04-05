from lib.data_collector import DataCollector
from scope import ping, executor, queries


class PingCtl(DataCollector):

    def __init__(self, stages=None, send_stages=None):
        """
        :param stages: list/tuple of stages name
        :param send_stages: list/tuple of stages name for sending to storage
        """
        self.create_key = 'create_ping_table'
        self.insert_key = 'insert_ping'
        if stages is None:
            stages = []
        if send_stages is None:
            send_stages = []
        self.stages = set(stages)
        self.send_stages = set(send_stages)
        super().__init__('ping', self.stages, self.send_to_storage)
        executor.execute_query(queries, self.create_key, commit=True)

    def start_listen(self):
        """
        Run listen cycle, use if you dont listen redis bus
        :return:
        """
        if hasattr(self.bus, 'listen'):
            if callable(self.bus.listen):
                self.bus.listen()

    def add_stage(self, name, send=False):
        """
        Add new stage or set send old stage
        :param name: str uniq stage name
        :param send: bool True if send stage ping to storage
        :return: None
        """
        if name not in self.required_keys:
            self.required_keys.add(name)
        if send and name not in self.send_stages:
            self.send_stages.add(name)

    def send_data(self, msg_id):
        """
        Call the self.fn function when all the data is collected
        """
        self.fn(**self._data[msg_id])
        self._data[msg_id] = dict()

    def send_to_storage(self, **kwargs):
        for key in kwargs.keys():
            if key in self.send_stages:
                executor.execute_query(queries, self.insert_key,
                                       stage=key, ts=kwargs[key], commit=True)
