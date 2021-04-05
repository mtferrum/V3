from lib.open_vino_model import FaceDetectorModel, FaceReidModel, LandmarksDetector
from lib.procrustes_face_aligner import align_face
from openvino.inference_engine import IEPlugin
import numpy as np
import cv2
import logging


log = logging.getLogger('spyspace')


class Infer:

    def __init__(self, mode='CPU', cpu_extension=None):
        self.vino_plugin = IEPlugin(mode)
        if mode == 'CPU':
            # Openvino 2019 and less
            try:
                if cpu_extension is None:
                    cpu_extension = "/opt/intel/openvino_2019.3.376/inference_engine/lib/intel64/libcpu_extension_avx512.so"
                self.vino_plugin.add_cpu_extension(cpu_extension)
            # Openvino 2020+
            except RuntimeError:
                pass
        self.detector = FaceDetectorModel(vino_plugin=self.vino_plugin)
        self.landmark = LandmarksDetector(vino_plugin=self.vino_plugin)
        self.reid = FaceReidModel(vino_plugin=self.vino_plugin)

    def infer_frame(self, frame):
        output_person = []
        faces_features = []
        initial_h, initial_w, initial_c = frame.shape
        # Execute Inference
        detector_res = self.detector.prepare_and_infer(frame)
        log.debug("infer Detection result: {}".format(detector_res.shape))
        for fk, obj in enumerate(detector_res[0][0]):
            prob_threshold = obj[2]
            if prob_threshold > 0.50:
                # Mapping NN face coordinates to frame's face coordinates
                xmin = int(obj[3] * initial_w)
                ymin = int(obj[4] * initial_h)
                xmax = int(obj[5] * initial_w)
                ymax = int(obj[6] * initial_h)
                xmin = xmin if xmin >= 0 else 0
                ymin = ymin if ymin >= 0 else 0
                xmax = xmax if xmax <= initial_w else initial_w
                ymax = ymax if ymax <= initial_h else initial_h

                # Cutting face from the frame
                cropped = frame[ymin:ymax, xmin:xmax]
                rgb_face = cropped[:, :, ::-1]
                landmark_res = self.landmark.prepare_and_infer(rgb_face)
                #log.info('landmark: {}'.format(landmark_res.shape))
                aligned_face = align_face(cropped, landmark_res[0])
                reid_res = self.reid.prepare_and_infer(aligned_face)
                #log.info('features: {}'.format(reid_res.shape))
                faces_features.append(reid_res)
                face_dict = {'initial': {'height': initial_h, 'width': initial_w},
                                  'left': xmin, 'top': ymin, 'right': xmax,
                                  'bottom': ymax}
                output_person.append(face_dict)

        if output_person:
            faces_features = np.vstack(faces_features)
            faces_features = faces_features.reshape(faces_features.shape[0], 256)
            for i in range(len(output_person)):
                output_person[i]['features'] = faces_features[i, :]
        return output_person
