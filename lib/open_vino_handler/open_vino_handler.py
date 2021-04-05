from lib.procrustes_face_aligner import align_face
from openvino.inference_engine import IEPlugin
import numpy as np
import cv2
import logging


log = logging.getLogger('spyspace')


class OpenVinoHandler:

    def __init__(self, mode='CPU', cpu_extension=None, classDetector=None, detector_model=None,
                 classLandmarks=None, landmarks_model=None, classReid=None, reid_model=None,
                 detection_threshold=0.50):
        self.vino_plugin = IEPlugin(mode)
        self.detector = None
        self.landmark = None
        self.reid = None
        if mode == 'CPU':
            # Openvino 2019 and less
            try:
                if cpu_extension is None:
                    cpu_extension = "/opt/intel/openvino_2019.3.376/inference_engine/lib/intel64/libcpu_extension_avx512.so"
                self.vino_plugin.add_cpu_extension(cpu_extension)
            # Openvino 2020+
            except RuntimeError:
                pass
        if classDetector is not None:
            self.detector = classDetector(vino_plugin=self.vino_plugin,
                                          model_file_name=detector_model)
            self.detection_threshold = detection_threshold
        if classLandmarks is not None:
            self.landmark = classLandmarks(vino_plugin=self.vino_plugin,
                                           model_file_name=landmarks_model)
        if classReid is not None:
            self.reid = classReid(vino_plugin=self.vino_plugin,
                                  model_file_name=reid_model)

    def infer_frame(self, frame):
        initial_h, initial_w, initial_c = frame.shape
        faces_rect = []
        faces_features = []
        # Execute Inference
        if self.detector is not None:
            detector_res = self.detector.prepare_and_infer(frame)
            log.debug("infer Detection result: {}".format(detector_res.shape))
            for fk, obj in enumerate(detector_res[0][0]):
                prob_threshold = obj[2]
                if prob_threshold > self.detection_threshold:
                    # Mapping NN face coordinates to frame's face coordinates
                    xmin = int(obj[3] * initial_w)
                    ymin = int(obj[4] * initial_h)
                    xmax = int(obj[5] * initial_w)
                    ymax = int(obj[6] * initial_h)
                    xmin = xmin if xmin >= 0 else 0
                    ymin = ymin if ymin >= 0 else 0
                    xmax = xmax if xmax <= initial_w else initial_w
                    ymax = ymax if ymax <= initial_h else initial_h
                    faces_rect.append((xmin, ymin, xmax, ymax))

                    if self.landmark is not None:
                        # Cutting face from the frame
                        cropped = frame[ymin:ymax, xmin:xmax]
                        rgb_face = cropped[:, :, ::-1]
                        landmark_res = self.landmark.prepare_and_infer(rgb_face)
                        aligned_face = align_face(cropped, landmark_res[0])
                    else:
                        aligned_face = None

                    if self.reid is not None and aligned_face is not None:
                        reid_res = self.reid.prepare_and_infer(aligned_face)
                        faces_features.append(reid_res)

        if faces_features:
            faces_features = np.vstack(faces_features)
            faces_features = faces_features.reshape(faces_features.shape[0], 256)
        return (initial_h, initial_w), faces_rect, faces_features
