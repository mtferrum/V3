import numpy as np
import json
from _datetime import datetime, timedelta
from scope import config, log, bus, executor, frame_handler, features_set, ram_bus, pedestrian_frame_handler
from lib.queries.mysql_queries import mysql_queries as query
import time


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


class Infer:

    def __init__(self, inertia_time=30, actual_time=120, query_pack_size=100):
        log.debug("infer Prepare MySQL environment")
        executor.execute_query(query, 'create_mvideo_db')
        executor.execute_query(query, 'use_mvideo_db')
        executor.execute_query(query, 'create_frames_table', commit=True)
        log.debug("infer MySQL environment prepared")
        self.black_threshold = config.find('identify_threshold')
        self.periods = []
        self.query_pack = []
        self.prev_alerts = {}
        self.query_pack_size = query_pack_size
        self.alert_inertia = timedelta(seconds=inertia_time)
        self.alert_actual = timedelta(seconds=actual_time)
        bus.subscribe('/pack_batches', self.unpack_pack)
        ram_bus.subscribe('/new_frames', self.receive_batch)
        bus.listen()

    def unpack_pack(self, pack):
        for el in pack:
            ts, batch_data = el
            ram_bus.push('/new_frames', ts, batch_data)

    def receive_batch(self, ts, batch_data):
        start = time.time()
        log.debug("infer Received processing batch data")
        all_persons = 0
        infer_time = []
        for i in range(len(batch_data)):
            camera_id = i
            frame = batch_data[i]['frame']
            filename = batch_data[i]['file_name']
            frame_number = batch_data[i]['index_number']
            faces_rect = None
            pedestrian_rect = None
            faces_features = None
            nearest = None
            if batch_data[i]['ret']:
                start_infer = time.time()
                initial, faces_rect, faces_features = frame_handler.infer_frame(frame)
                initial_pedestrian, pedestrian_rect, *_ = pedestrian_frame_handler.infer_frame(frame) # NEW
                end_infer = time.time()
                infer_time.append(end_infer - start_infer)
            if faces_rect:
                init_height, init_width = initial
                now = datetime.now()
                all_persons += len(faces_rect)
                if (now - ts) < self.alert_actual:
                    #log.info('set: {} path: {}'.format(features_set.p.get_ids_list(), features_set.output_path))
                    nearest = features_set.find_nearest(faces_features)
                for j in range(len(faces_rect)):
                    l, t, r, b = faces_rect[j]
                    if nearest is not None:
                        label = nearest[0][j]
                        distance = nearest[1][j]
                        self.alert_send(now, ts, camera_id, label, distance, l, t, r, b,
                                        filename, frame_number, frame)
            # NEW
            if pedestrian_rect:
                init_ped_w, init_ped_h = initial_pedestrian
                for j in range(len(pedestrian_rect)):
                    lp, tp, rp, bp = pedestrian_rect[j]
                    self.storage_save(camera_id, ts, lp, tp, rp, bp, filename, frame_number,
                                      init_ped_h, init_ped_w)
            continue
        end = time.time()
        self.periods.append(end - start)
        if len(self.periods) > 1000:
            avg_period = sum(self.periods) / len(self.periods)
            self.periods = []
            log.info("infer Output persons : {}, ts: {}".format(all_persons, ts))
            log.info('infer cycle total FPS = {}, infer FPS = {}'.format(1/avg_period, 1/sum(infer_time)))

    def alert_send(self, now, ts, camera_id, label, distance, l, t, r, b, filename,
                   frame_number, frame):
        #log.info('sender dist {}'.format(distance))
        if distance >= self.black_threshold:
            prev_alert = self.prev_alerts.get(label)
            if prev_alert is not None:
                if (ts - prev_alert) >= self.alert_inertia:
                    self.prev_alerts.pop(label, None)
                else:
                    self.prev_alerts[label] = now

            prev_alert = self.prev_alerts.get(label)
            if prev_alert is None:
                bus.push('/danger', ts, camera_id, label, distance,
                         l, t, r, b, filename, frame_number, frame)
                self.prev_alerts[label] = now

    def storage_save(self, camera_id, ts, l, t, r, b, filename, frame_number, #features,
                     init_height, init_width):
        # Convert ndarray to json
        #features = json.dumps(features, cls=NumpyEncoder)
        #assert type(features) == str, "Features is not converted to JSON data type"
        # Query inserting Output Person data
        features = None
        if len(self.query_pack) >= self.query_pack_size:
            executor.execute_query(query, 'insert_many_frames',
                                   self.query_pack, many=True, commit=True)
            self.query_pack = []
        else:
            self.query_pack.append((camera_id, ts, l, t, r, b, filename, frame_number,
                                    features, init_height, init_width, l / init_width,
                                    t / init_height, r / init_width, b / init_height))
