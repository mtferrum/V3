from scope import bus, config, log, messenger, executor
from lib.queries.mysql_queries import mysql_queries as queries
import os
import cv2
from datetime import datetime, timedelta


class Alerter:

    def __init__(self, inertia_time=30):
        self.prev_alerts = {}
        self.alert_inertia = timedelta(seconds=inertia_time)
        self.photos_dir = config.find('photos_dir')
        executor.execute_query(queries, 'create_alerts_table', commit=True)
        executor.execute_query(queries, 'create_telegram_subscribers_table', commit=True)
        try:
            executor.execute_query(queries, 'alter_is_tester_alerts_table', commit=True)
        except Exception as e:
            log.debug(e)
        try:
            executor.execute_query(queries, 'alter_is_tester_faces_table', commit=True)
        except Exception as e:
            log.debug(e)
        try:
            executor.execute_query(queries, 'alter_bot_telegram_subscribers_table', commit=True)
        except Exception as e:
            log.debug(e)
        blacklist_alert = """<b>Посетитель из черного списка: </b> 
        Идентификатор: {} 
        Похожесть: {}%, Камера: {}
        Время: {}"""
        whitelist_alert = """<b>Посетитель из белого списка: </b> 
        Идентификатор: {} 
        Похожесть: {}%, Камера: {}
        Время: {}"""
        messenger.add_mailing_template('blacklist', blacklist_alert)
        messenger.add_mailing_template('whitelist', whitelist_alert)
        bus.subscribe('/danger', self.receive_alert)
        bus.listen()

    def _image_prepared(self, image, rect=None):
        try:
            if isinstance(image, str):
                image = cv2.imread(image)
            if rect:
                cv2.rectangle(image, rect[0:2:], rect[2::], (0, 0, 255), 1)
            retval, image = cv2.imencode('.jpg', image)
        except cv2.error as e:
            image = None
            log.warning('alerter Did not prepare image with error: {}'.format(e))
        return image

    def receive_alert(self, ts, camera, label, distance, left, top, right, bottom,
                      filename, frame_number, frame):
        now = datetime.now()
        prev_alert = self.prev_alerts.get(label)
        if prev_alert is not None:
            if (ts - prev_alert) >= self.alert_inertia:
                self.prev_alerts.pop(label, None)
            else:
                self.prev_alerts[label] = now

        prev_alert = self.prev_alerts.get(label)
        if prev_alert is None:
            photo_files, is_tester = executor.execute_query(queries, 'select_filename_by_id',
                                                            label=label)[0]
            if is_tester:
                bot = 'whitelist'
            else:
                bot = 'blacklist'

            frame = self._image_prepared(frame, (left, top, right, bottom))
            if photo_files:
                origin_filename = photo_files
                origin_path = os.path.join(self.photos_dir, origin_filename)
                origin = self._image_prepared(origin_path)
            else:
                origin_filename = 'None'
                origin = None

            log.info('alerter Sending alert message for label {}...'.format(label))
            messenger.subscribers = [sub[0] for sub in
                                     executor.execute_query(queries,
                                                            'select_telegram_subscribers_unmute',
                                                            bot=bot)]
            send_alert = messenger.send_mailing(bot, label, int(distance * 100), camera,
                                                ts, frame=frame, origin=origin)
            try:
                while True:
                    res, user_id = next(send_alert)
                    if res == 403:
                        executor.execute_query(queries, 'telegram_subscriber_mute',
                                               user_id=user_id, commit=True)
            except StopIteration:
                log.info('alerter Sent alert message for label {} to messenger'.format(label))

            executor.execute_query(queries, 'insert_alerts_table', camera_id=camera,
                                   ts=ts, l=left, t=top, r=right, b=bottom, label=label,
                                   distance=distance, frame_number=frame_number,
                                   filename=filename, origin=origin_filename,
                                   is_tester=is_tester, commit=True)
            log.info('alerter Sent alert for label {} to database'.format(label))
            self.prev_alerts[label] = now
