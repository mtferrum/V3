import datetime
import time
from scope import config, executor, tracker, log, queries


class TrackerCtl:

    def __init__(self):
        self.tracker = tracker
        self.executor = executor

        self.download_interval = datetime.timedelta(seconds=config.find('counter/download_interval'))
        self.track_max_lag = datetime.timedelta(minutes=config.find('counter/track_max_lag'))
        self.select_limit = config.find('counter/select_limit')

        self._select_from_frames = 'select_frames_tracker'
        self._select_from_tracks = 'select_tracks_tracker'
        self._update_frames_status = 'update_frames_status'
        self._update_tracks = 'update_tracks_tracker'
        self._insert_into_tracks = 'insert_tracks_tracker'
        self._create_frames_table = 'create_frames_table'
        self._create_tracks_table = 'create_tracks_table'
        #  creating tables is not exists
        self.executor.execute_query(queries, self._create_frames_table)
        self.executor.execute_query(queries, self._create_tracks_table)

        self._prev_time = datetime.datetime.now()
        self.frames = self.executor.execute_query(queries, self._select_from_frames, limit=self.select_limit, commit=True)
        self.preload_tracks(self._prev_time)
        self.preload_ids = self.tracker.get_all_track_ids()

    def preload_tracks(self, timestamp):
        tracks = self.executor.execute_query(queries, self._select_from_tracks, time=timestamp - self.track_max_lag, commit=True)
        for track in tracks:
            track_id, l0, t0, r0, b0, ts0, filename0, frame0, l1, t1, r1, b1, ts1, filename1, frame1, length, camera_id = track  # IN THIS ORDER! CRITICAL!
            self.tracker.fill_storage(track_id, (l0, t0, r0, b0, ts0, filename0, frame0), (l1, t1, r1, b1, ts1, filename1, frame1), length, camera_id)
        del tracks

    def process_frames(self):
        log.info('Tracker starting processing frames')
        while True:
            now = datetime.datetime.now()
            if now - self._prev_time >= self.download_interval:
                self.frames = self.executor.execute_query(queries, self._select_from_frames, limit=self.select_limit, commit=True)
                self.preload_tracks(now)
                self.preload_ids = self.tracker.get_all_track_ids()
                self._prev_time = now
            if self.frames:
                oldest_frame_ts = self.frames[-1][1]  # FIX THIS
                processed = 0
                total_frames = len(self.frames)
                while self.frames:
                    camera_id, ts, l, t, r, b, filename, frame_num = self.frames.pop(0)
                    self.tracker.add_track(l, t, r, b, ts, filename, frame_num, camera_id)
                    processed += 1
                log.info('Tracker processed {} out of {} total frames'.format(processed, total_frames))
                self.executor.execute_query(queries, self._update_frames_status, oldest=oldest_frame_ts, commit=True)
                log.info('Tracker frames table updated')

                for track_id in self.preload_ids:
                    track = self.tracker.get_track(track_id)
                    l1, t1, r1, b1, ts1, filename1, frame1 = track['last']
                    length = track['length']
                    self.executor.execute_query(queries, self._update_tracks,
                                                track_id=str(track_id),
                                                l1=l1,
                                                t1=t1,
                                                r1=r1,
                                                b1=b1,
                                                ts1=ts1,
                                                filename1=filename1,
                                                frame1=frame1,
                                                len=length,
                                                commit=True)

                new_ids = self.tracker.get_all_track_ids() - self.preload_ids
                for track_id in new_ids:
                    track = self.tracker.get_track(track_id)
                    l0, t0, r0, b0, ts0, filename0, frame0 = track['first']
                    l1, t1, r1, b1, ts1, filename1, frame1 = track['last']
                    length = track['length']
                    camera_id = track['camera_id']
                    self.executor.execute_query(queries, self._insert_into_tracks,
                                                track_id=str(track_id),
                                                l0=l0,
                                                t0=t0,
                                                r0=r0,
                                                b0=b0,
                                                ts0=ts0,
                                                filename0=filename0,
                                                frame0=frame0,
                                                l1=l1,
                                                t1=t1,
                                                r1=r1,
                                                b1=b1,
                                                ts1=ts1,
                                                filename1=filename1,
                                                frame1=frame1,
                                                len=length,
                                                camera_id=str(camera_id),
                                                commit=True)

                log.info('Tracker inserted {} tracks into table'.format(len(new_ids)))
                self.tracker.empty_storage()
                self.frames = []
                log.info('Tracker full cycle finished')
            time.sleep(1)
