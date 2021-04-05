import datetime
from uuid import uuid4
from .intersect_over_union import iou


class IouBoxTracker:
    """
    Forms tracks from sequence of rectangles and timestamps

    self._storage = {track_id(uuid4): (l, t, r, b, timestamp), track_id(uuid4): (l, t, r, b, timestamp2), ...]}
    self.iou_threshold = float from 0 to 1
        Minimum intersect-over-union ratio of two bounding boxes
    self.lag = datetime.timedelta
        Maximum time before one box can be related to some track or not
    """
    _storage = dict()

    def __init__(self, threshold=.3, lag=3):
        self.iou_threshold = threshold
        self.lag = datetime.timedelta(seconds=lag)

    def add_track(self, l, t, r, b, ts, filename, frame_num, camera_id):
        """
        Tracks bounding boxes in respect to timestamp with predefined lag

        :param l: Float coordinates of left side of a rectangle
        :param t: Float coordinates of top side of a rectangle
        :param r: Float coordinates of right side of a rectangle
        :param b: Float coordinates of bottom side of a rectangle
        :param ts: datetime.datetime object
        :param filename String containing name of file where to track is written
        :param frame_num Int correponds to a frame number in video file for specific frame
        :param camera_id: String name of camera from which frame originated
            Time coordinated of a rectangle
        :return:

        Tests:
        1) new track
        2) track exists
        3) more than 2 nearest => select the best
        """
        track_id = None
        if all([l, t, r, b, ts, camera_id]):
            if r > l and b > t:
                track_id = uuid4()
                score_max = 0
                for key, frames in self._storage.items():
                    x0, y0, x1, y1, old_timestamp, *_ = frames['last']
                    score = iou((l, t, r, b), (x0, y0, x1, y1))
                    if self.iou_threshold <= score and self.lag >= ts - old_timestamp and score > score_max \
                            and frames['camera_id'] == camera_id:
                        track_id = key
                        score_max = score
                if not score_max:
                    self._storage[track_id] = {'first': (l, t, r, b, ts, filename, frame_num),
                                               'last': (l, t, r, b, ts, filename, frame_num),
                                               'length': 1,
                                               'camera_id': camera_id}
                else:
                    self._storage[track_id]['last'] = (l, t, r, b, ts, filename, frame_num)
                    self._storage[track_id]['length'] += 1
        return track_id

    def fill_storage(self, track_id, first, last, length, camera_id):
        """
        Used to iteratively fill _storage with data

        :param track_id: Str or uuid4
        :param first: Tuple(l, t, r, b, timestamp, filename, frame_num)
        :param last: Tuple(l, t, r, b, timestamp, filename, frame_num)
        :param length: Int summary number of frames in tracks
        :param camera_id: String of unique camera identifier
        :return: True on success, False on fail
        """
        result = False
        if isinstance(track_id, str) and isinstance(first, tuple) and isinstance(last, tuple) \
                and isinstance(length, int) and isinstance(camera_id, str):
            self._storage[track_id] = {'first': first, 'last': last, 'length': length, 'camera_id': camera_id}
            result = True
        return result

    def empty_storage(self):
        self._storage = dict()

    def get_all_track_ids(self):
        return set(self._storage.keys())

    def get_track(self, track_id):
        return self._storage[track_id]
