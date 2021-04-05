from flask import Flask, redirect
from scope import config, log, executor, queries
import math
import cv2
import os


log.info('reporter Initializing Flask...')
app = Flask(__name__)
log.info('reporter Flask initialized')

URI = config.find('reporter/uri', '/')
VIDEOS_PATH = config.find('reader/videos_path')
IMAGE_PATH = config.find('reporter/image_path')

@app.route("/reporter/get_direction/<track_id>")
def get_direction(track_id):
    try:
        select_track = 'select_tracks_reporter'
        track = executor.execute_query(queries, select_track, track_id=track_id, commit=True)
        if track:
            l0_f, t0_f, r0_f, b0_f, ts0, filename0, frame0, l1_f, t1_f, r1_f, b1_f, ts1, filename1, frame1, length, camera_id = track.pop()
        else:
            return 'TRACK WITH THIS ID={} DOES NOT EXIST'.format(track_id)
        image_file = '{path}/{track_id}.jpg'.format(path=IMAGE_PATH, track_id=track_id)
        f0 = '{path}/{filename0}'.format(path=VIDEOS_PATH, filename0=filename0)
        f1 = '{path}/{filename1}'.format(path=VIDEOS_PATH, filename1=filename1)
        if os.path.exists(f1):
            if not os.path.exists(image_file):
                cap = cv2.VideoCapture(f1)
                cap.set(1, int(frame1))  # set frame position in video
                width = int(cap.get(3))
                height = int(cap.get(4))
                ret, image = cap.read()
                if not ret:
                    return 'CANNOT READ FILE'

                from_w = (l0_f, r0_f, l1_f, r1_f)
                from_h = (t0_f, b0_f, t1_f, b1_f)
                l0, r0, l1, r1 = tuple(int(x*width) for x in from_w)
                t0, b0, t1, b1 = tuple(int(x*height) for x in from_h)
                dist = math.sqrt((r1 - r0)**2 + (b1 - b0)**2)
                if dist:
                    angle_x = math.acos((r1 - r0) / dist) * (180 / math.pi)
                    angle_y = math.acos((b1 - b0) / dist) * (180 / math.pi)
                    cv2.putText(image, 'Angle_x:{}, Angle_y:{}'.format(angle_x, angle_y),
                                (20, 120),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0))
                cv2.rectangle(image, (l0, t0), (r0, b0), (0, 255, 0), 2)
                cv2.rectangle(image, (l1, t1), (r1, b1), (0, 255, 0), 2)
                cv2.arrowedLine(image, (r0 - ((r0 - l0) // 2), b0 - ((b0 - t0) // 2)), (r1 - ((r1 - l1) // 2), b1 - ((b1 - t1) // 2)), (255, 255, 0), 5)
                cv2.putText(image, 'First timestamp:{}'.format(ts0),
                            (20, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0))
                cv2.putText(image, 'Last timestamp:{}'.format(ts1),
                            (20, 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0))
                cv2.putText(image, 'Dist:{}, Track length:{}'.format(dist, length),
                            (20, 90),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0))
                cv2.imwrite(image_file, image)
        else:
            return 'CANNOT FIND VIDEOFILE={}'.format(f1)

        return redirect('{uri}frames/{track_id}.jpg'.format(uri=URI, track_id=track_id))
    except Exception as e:
        return str(e)

@app.route("/reporter/test")
def test_reporter():
    """
    Simple function that helps eliminate problems with uwsgi.

    Usage example:
        http://localhost/reporter/test in browser will output return string.
    :return: String
    """
    return "uwsgi working! Test successfull"


if __name__ == "__main__":
    log.info('reporter Starting server...')
    app.run(host='localhost', port=1337)
    log.info('reporter Server started, serving forever')
