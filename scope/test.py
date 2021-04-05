# Basic scope for test
from lib.yaml_config import YamlConfig as Config
from lib.hnsw_features_set import HNSWFeaturesSet
from lib.procrustes_face_aligner import align_face
from lib.open_vino_model import FaceDetectorModel, FaceReidModel, LandmarksDetector
from lib.mysql_driver.mysql_engine import MySQLEngine
from lib.query_executor.query_executor import QueryDictExecutor
from lib.redis_bus import RedisBus
from lib.telegram import Telegram
from lib.basic_logger import log


# Create global instance of config
project_dir = "/opt/projects/mvid"
# project_dir = "/home/tech/PycharmProjects/mvid"
config = Config(project_dir + '/scope/data/test_conf.yaml')
# Create global instance of basic transport
bus = RedisBus()
redis = RedisBus()
executor = QueryDictExecutor(MySQLEngine, config.find('mysql_host'),
                             user=config.find('mysql_user'),
                             password=config.find('mysql_passwd'))
features_set = HNSWFeaturesSet(config.find('ann_path'), config.find('ann_max_elements'))
reid_tree = HNSWFeaturesSet(config.find('ann_path'), config.find('ann_max_elements'))
detector = FaceDetectorModel()
landmark = LandmarksDetector()
reid = FaceReidModel()
messenger = Telegram(token=config.find('telebot_token'), proxy=config.find('proxy'),
                     password=config.find('telebot_password'))

