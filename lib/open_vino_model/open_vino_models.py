from .open_vino_base_model import OpenVinoModel
import sys
import os


class FaceDetectorModel(OpenVinoModel):
    model = 'component/infer/model/face-detection-retail-0004/FP32-INT8/face-detection-retail-0004.xml'
    MODEL_FILE_NAME = os.path.join(sys.path[0], *model.split('/'))


class FaceReidModel(OpenVinoModel):
    model = 'component/infer/model/face-reidentification-retail-0095/FP32-INT8/face-reidentification-retail-0095.xml'
    MODEL_FILE_NAME = os.path.join(sys.path[0], *model.split('/'))


class LandmarksDetector(OpenVinoModel):
    model = 'component/infer/model/landmarks-regression-retail-0009/FP32-INT8/landmarks-regression-retail-0009.xml'
    MODEL_FILE_NAME = os.path.join(sys.path[0], *model.split('/'))
