import cv2
import sys
import os
import time
from threading import Thread, Lock
from datetime import datetime, timedelta
from scope import config, log, bus, bus2, ping


class ReaderStreams:

    def __init__(self, streams=None, timeout=1, fps=25, file_time=60):
        self.videos_dir = config.find('videos_path')
        self.standby = cv2.imread(os.path.join(sys.path[0],
                                               *config.find('standby').split('/')))
        self.timeout = timedelta(milliseconds=timeout)
        self.file_time = config.find('video_duration') or file_time
        self.fps = config.find('framerate') or fps
        self.ext = config.find('ext') or 'avi'
        self.ts_start = None
        self.caps_list = []
        self.list_to_push = []
        self.lock = Lock()
        for stream in config.find('streams') or streams:
            log.info('reader Processing stream {}'.format(stream))
            cap = {}
            cap['stream'] = stream
            cap['cap'] = cv2.VideoCapture(stream, cv2.CAP_GSTREAMER)
            cap['cap'].set(3, 300)
            cap['cap'].set(4, 300)
            cap['width'] = 300
            cap['height'] = 300
            cap['standby'] = cv2.resize(self.standby, (cap['width'], cap['height']))
            cap['time_off'] = None
            cap['writer'] = None
            self.caps_list.append(cap)

    def corrupted_cap(self, cap):
        if cap['time_off'] is None:
            cap['time_off'] = datetime.now()
        else:
            delta = datetime.now() - cap['time_off']
            if delta >= self.timeout:
                cap['cap'] = cv2.VideoCapture(cap['stream'], cv2.CAP_GSTREAMER)
                cap['time_off'] = None

    def iter_frame(self):
        for cap_id in range(len(self.caps_list)):
            cap = self.caps_list[cap_id]
            ret = False
            if cap['cap'].isOpened():
                ret, frame = cap['cap'].read()
            if ret:
                inst_frame = frame.copy()
            else:
                inst_frame = cap['standby']
                self.corrupted_cap(cap)
            yield cap_id, ret, inst_frame

    def iter_batch(self):
        frame_index = 0
        ts_start = datetime.now()
        while True:
            batch_data = []
            ts = datetime.now()
            frame = self.iter_frame()
            ping.ping_stage('reader', start=True, final=True)
            try:
                while True:
                    frame_dict = {}
                    cap_id, ret, inst_frame = next(frame)
                    frame_dict['file_name'] = 'Cam{}_{}.{}'.format(cap_id, ts_start, self.ext)
                    frame_dict['index_number'] = frame_index
                    frame_dict['frame'] = cv2.resize(inst_frame, (300, 300))
                    frame_dict['ret'] = ret
                    self.write_videos(cap_id, ts, frame_dict)
                    batch_data.append(frame_dict)
            except StopIteration:
                if frame_index == (self.fps * self.file_time):
                    frame_index = 0
                    ts_start = datetime.now()
                else:
                    frame_index += 1
                yield ts, batch_data

    def write_videos(self, cap_id, ts, frame_dict):
        cap = self.caps_list[cap_id]
        if frame_dict['index_number'] == 0:
            self.ts_start = ts
            file = os.path.join(self.videos_dir, frame_dict['file_name'])
            log.info('reader Starting write video for '
                     'stream: {} filename: {}...'.format(cap_id, file))
            cap['writer'] = cv2.VideoWriter(file, #cv2.CAP_INTEL_MFX,
                                            cv2.VideoWriter_fourcc('H', '2', '6', '4'),
                                            self.fps, (self.caps_list[cap_id]['width'],
                                                       self.caps_list[cap_id]['height']))
        cap['writer'].write(frame_dict['frame'])
        if frame_dict['index_number'] == (self.fps * self.file_time):
            cap['writer'].release()
            log.info('reader Finished write video for stream: {}.'.format(cap_id))

    def run_streams(self):
        def push_to_bus(bus):
            while True:
                if len(self.list_to_push) > 0:
                    send_list = self.list_to_push.pop()
                    bus.push('/pack_batches', [send_list])
                else:
                    time.sleep(0.01)

        iter_batch = self.iter_batch()
        periods = []
        push_thread1 = Thread(target=push_to_bus, args=(bus,))
        push_thread2 = Thread(target=push_to_bus, args=(bus2,))
        push_thread1.start()
        push_thread2.start()
        while True:
            start = time.time()
            ts, batch_data = next(iter_batch)
            self.list_to_push.insert(0, (ts, batch_data))
            end = time.time()
            period = end - start
            periods.append(period)
            if len(periods) > 1000:
                avg_period = sum(periods) / len(periods)
                periods = []
                log.info('reader FPS = {}, queue = {} '.format((1 / avg_period), len(self.list_to_push)))

