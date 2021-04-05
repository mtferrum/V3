from openvino.inference_engine import IENetwork
import cv2
import time
import logging


log = logging.getLogger('spyspace')


class OpenVinoModel:
    """ Toolkit for Abstract OpenVINO model
    """
    MODEL_FILE_NAME = None

    def __init__(self, vino_plugin=None, model_file_name=None):
        """
        All the model attributes
        :param model_file_name:
        """
        if model_file_name is None:
            self.net_config = IENetwork(model=self.MODEL_FILE_NAME, weights=self.MODEL_FILE_NAME[:-4] + '.bin')
        else:
            self.net_config = IENetwork(model=model_file_name, weights=model_file_name[:-4] + '.bin')

        self.outputs = [i for i in iter(self.net_config.outputs)]
        self.input = next(iter(self.net_config.inputs))
        self.shape = self.net_config.inputs[self.input].shape
        self.batch, self.channels, self.height, self.width = self.shape
        self.exec = None
        if vino_plugin is not None:
            self.exec_load(vino_plugin)

    def exec_load(self, vino_plugin):
        self.exec = vino_plugin.load(network=self.net_config)

    def infer(self, frame):
        """
        IO method for OpenVINO model
        :param frame: CV2 frame
        :return: (float) result OR (list) results
        """
        self.exec.infer(inputs={self.input: frame})
        results = []
        for output in self.outputs:
            results.append(self.exec.requests[0].outputs[output])
        # For single-sized outputs return float, else list
        if len(results) == 1:
            return results[0]
        return results

    def prepare_and_infer(self, frame):
        """
        Prepare OpenVINO models input shape from a frame
        Then infer
        :param frame: CV2 frame
        :return: (float) result OR (list) results
        """
        if frame.shape[0] != self.width or frame.shape[1] != self.height:
            in_frame1 = cv2.resize(frame, (self.width, self.height))  # return np [height:width:channels]
        else:
            in_frame1 = frame
        in_frame2 = in_frame1.transpose((2, 0, 1))  # HWC to CHW, return np [channels:height:width]
        in_frame3 = in_frame2.reshape((self.batch, self.channels, self.height, self.width))
        res = self.infer(in_frame3)
        del in_frame1, in_frame2, in_frame3
        return res
