import os
import cv2
import hnswlib
import numpy as np
import logging
from datetime import datetime, timedelta

log = logging.getLogger('spyspace')


class HNSWFeaturesSet:

    def __init__(self, output_path='', max_elements=2000, dim=256, timeout=5,
                 threads_num=None):
        self.max_elements = max_elements
        self.dim = dim
        self.output_path = output_path
        self.reload_timeout = timedelta(minutes=timeout)
        log.info('Creating {}-dim index...'.format(self.dim))
        self.p = hnswlib.Index(space='cosine', dim=dim)
        if os.path.exists(self.output_path):
            log.info('Loading index...'.format())
            self.p.load_index(self.output_path)
            log.info('Load index'.format())
        else:
            log.info('Initialising index...'.format())
            self.p.init_index(max_elements=self.max_elements)
        self.prev_mod_time = datetime.fromtimestamp(os.path.getmtime(self.output_path))
        self._update_file(self.p)
        if not os.path.exists(self.output_path):
            raise FileNotFoundError("File {} not found".format(self.output_path))
        if threads_num:
            log.debug('Setting number of threads to {}...'.format(threads_num))
            self.p.set_num_threads(threads_num)

    def _reload_modify(self):
        for i in range(2):
            if os.path.exists(self.output_path):
                new_mod_time = datetime.fromtimestamp(os.path.getmtime(self.output_path))
                if self.prev_mod_time:
                    is_mod = new_mod_time != self.prev_mod_time
                    if is_mod:
                        self.prev_mod_time = new_mod_time
                        log.info('Reloading index...'.format())
                        self.p.load_index(self.output_path)
                else:
                    self.prev_mod_time = new_mod_time
            else:
                if i == 1:
                    raise FileNotFoundError("File {} not found".format(self.output_path))
                else:
                    continue

    def _update_file(self, index):
        log.info('Saving index with length {} to {}...'.format(len(self), self.output_path))

        index.save_index(self.output_path)
        log.info('Index saved'.format(self.output_path))

    def rebuild(self, features, list_ids):
        """Rebuild tree and update file

        Accepts
        -------
        :param features: list of 256-dim nparrays/nparray with shape (len, 256)
        :param list_ids: list of ints of the same length as features

        """
        assert (len(features) == len(list_ids))
        assert (len(list_ids) == len(set(list_ids)))
        new_index = hnswlib.Index(space='cosine', dim=self.dim)
        new_index.init_index(max_elements=self.max_elements)
        log.debug('Rebuilding index of length {}, new length = {}...'.format(len(self), len(list_ids)))
        if len(features):
            new_index.add_items(features, list_ids)
        self.p = new_index
        self._update_file(new_index)

    def find_nearest(self, features):
        self._reload_modify()
        if len(self) > 0:
            list_id, distances = self.p.knn_query(features, k=1)
            return list_id[:, 0], 1 - distances[:, 0]
        else:
            return None

    def __len__(self):
        return len(self.p.get_ids_list())
