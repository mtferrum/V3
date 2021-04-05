import logging
import yaml
import copy
from uuid import uuid4
from yaml import Loader
import sys


log = logging.getLogger('spyspace')


class NotFoundException(BaseException):
    """No result message for recursive method
    """


class FoundException(BaseException):
    """Transport for data in recursive method
    """

    def __init__(self, data, *args, **kwargs):
        """ Store data as-is in self.data
        """
        self.data = data
        super().__init__(data, *args, **kwargs)


class YamlConfig:
    """A class to search for parameters and their values in YAML config files.

    Usage example:
        conf_file = 'test_config.yaml'
        config = Config(conf_file)
    Get the value by a part of its path:
        val = config.find('face/MIN_MOTION_THRESHOLD',  'No such a key found')
    Get the full path to key by a part:
        path = config.get_path('face/MIN_MOTION_THRESHOLD', 'Fail =(')
    As a dict:
        INTEL_LM_MODEL = config.data['cnn']['INTEL_LM_MODEL']
    Update a value in RAM:
        config.update_param('face/MIN_MOTION_THRESHOLD', 1)
    Update a value in YAML:
        config.update_param('face/MIN_MOTION_THRESHOLD', 1, commit=True)
    """

    def __init__(self, conf_file):
        """
        :param conf_file: (str) file to load from
        """
        self.conf_file = conf_file
        self.data = dict()
        self._sub_dict = dict()
        self._fullpath = list()
        self._needle = str()
        self.iter_counter = 0
        self.load_data()
        log.info('config Audit for {}...'.format(conf_file))
        self._all_paths = dict()
        self.audit()
        log.info('config Finished audit for {}'.format(conf_file))
        self.argv = dict()
        self.get_argv()

    def get_argv(self):
        for pair in sys.argv[2:]:
            k, v = pair.split('=')
            self.argv[k] = v

    def load_data(self, _conf_file=None):
        """Load or reload data from a file
        :param _conf_file: (str) file to load from
        :return: True on success
        """
        conf_file = _conf_file or self.conf_file
        log.info('config Loading from {}...'.format(conf_file))
        with open(conf_file, 'r', encoding='utf8') as config_stream:
            config_data = yaml.load(config_stream, Loader=Loader)
        self.data = config_data
        self._sub_dict = config_data
        log.info('config Loaded from {}'.format(conf_file))
        return True

    def save_data(self, _conf_file=None):
        """Save data to a file
        :param _conf_file: (str) file to save to
        :return: True on success
        """
        conf_file = _conf_file or self.conf_file
        log.info('config Saving to {}...'.format(conf_file))
        with open(conf_file, 'w', encoding='utf8') as outfile:
            yaml.dump(self.data, outfile, default_flow_style=False)
        log.info('config Saved to {}'.format(conf_file))
        return True

    def _iterdict(self, d=None, prev=''):
        """Recursive method to search recursively for a value in the dict
        :param d: (dict) A dictionary where to search to
        :param prev: (str) A key in path chain
        :raises: FoundException with data param storing result on success
        :returns: None on fail
        """
        if d is None:
            d = self._sub_dict
        self._fullpath.append(str(prev))
        for k, v in d.items():
            if isinstance(k, (str, int)):
                self.iter_counter += 1
                found = True
                for i in self._needle.split('/'):
                    if str(i).lower() != str(k).lower():
                        found = False
                        break
                if found:
                    self._fullpath.append(str(k))
                    raise FoundException(v)

            if isinstance(v, dict):
                self._iterdict(v, k)
        self._fullpath.pop()

    def audit(self, d=None, prev=''):
        """Recursive method to find duplicate keys in config
        :param d: (dict) A dictionary where to search to
        :param prev: (str) A key in path chain
        :returns: None
        """
        if d is None:
            d = self.data
        self._fullpath.append(prev)
        for k, v in d.items():
            if isinstance(v, dict):
                self.audit(v, k)
            else:
                path = '/'.join(self._fullpath)
                if k in self._all_paths.keys() and 'logging' not in path:
                    log.warning('config Key {} ({}) duplicates in path {}'.format(k, self._all_paths[k], path))
                self._all_paths[k] = path
        self._fullpath.pop()

    def _find_key(self, needle, d=None):
        """Search recursively for a value in the dict by a key
        :param needle: (str) Key to find a value
        :param d: (dict) A dictionary where to search to
        :return: value on success
        :raises: NotFoundException on fail
        """
        self._sub_dict = d or self.data
        self._needle = needle
        self.iter_counter = 0
        log.debug('config Searching for {}...'.format(needle))
        try:
            self._iterdict()
        except FoundException as e:
            log.debug('config Found key {} by {} iterations'.format(
                needle, self.iter_counter))
            return e.data

        log.debug('config Not found key {} by {} iterations'.format(
                needle, self.iter_counter))
        raise NotFoundException(
            'Key {} not found in {}'.format(needle, self.conf_file))

    def find(self, needles, default=None):
        """Search for a value in config by a path
        :param needles: (str) Needles hierarchically divided by slash
               e.g.: 'mqtt/clientid'
        :param default: (object) What to return if no result
        :return: value or default
        """
        needles = str(needles)
        # first, try to get from argv
        if needles in self.argv.keys():
            return self.argv[needles]

        data_new = copy.deepcopy(self)
        log.info('config Searching for {} in {}...'.format(needles,
                                                            data_new.conf_file))
        sub_dict = None
        data_new._fullpath = list()
        for needle in needles.split('/'):
            try:
                result = data_new._find_key(needle, sub_dict)
            except NotFoundException as e:
                log.info('config Not found key {} in {}'.format(needle,
                                                           data_new.conf_file))
                return default
            if not isinstance(result, dict):
                break
            sub_dict = result
        path = '/'.join(data_new._fullpath)
        log.info('config Found {} by {} in {}'.format(path, needles,  self.conf_file))
        self._fullpath = data_new._fullpath
        return result

    def get_path(self, needle, default=None):
        """Search for a path to the key in config by a path
               e.g.: 'mqtt/clientid'
        :param needle: (str) Needles hierarchically divided by slash
        :return: full path to key or default
        """
        log.info('config Searching for full path for {} in {}...'.format(
            needle, self.conf_file))
        _not_found = uuid4()
        result = self.find(needle, _not_found)
        if result is _not_found:
            log.info('config Path not found for {}'.format(needle))
            return default

        path = '/'.join(self._fullpath)
        log.info('config Found path {} for {}'.format(path, needle))
        return path

    def update_param(self, needle, new_value, commit=False):
        """
        :param needle: (str) Needles hierarchically divided by slash
        :param new_value: (object) Value to write
        :param commit: (bool) Save changes to YAML file or not
        :return: (bool) True if success
        :raises: NotFoundError if key not found
        """
        log.info('config update Searching for path {} in {}...'.format(
            needle, self.conf_file))
        _not_found = uuid4()
        result = self.find(needle, _not_found)
        if result is _not_found:
            log.warning('config update Path not found for {}'.format(needle))
            raise NotFoundException(
                'Key {} not found in {}'.format(needle, self.conf_file))

        path = '/'.join(self._fullpath)
        log.info('config update Updating key {} set {}...'.format(
            path, new_value))
        branch = self.data
        for child in self._fullpath[:-1]:
            if child:
                branch = branch[child]
        branch[self._fullpath[-1]] = new_value
        if commit:
            self.save_data()
        log.info('config update Updated key {} to {}'.format(path, new_value))
        return True
