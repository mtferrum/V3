# Basic scope for NUC
from lib.yaml_config import YamlConfig as Config
from lib.hnsw_features_set import HNSWFeaturesSet
from lib.open_vino_handler import OpenVinoHandler
from lib.open_vino_model import FaceDetectorModel, FaceReidModel, LandmarksDetector
from lib.mysql_driver.mysql_engine import MySQLEngine
from lib.query_executor.query_executor import QueryDictExecutor
from lib.redis_bus import RedisBus
from lib.ram_bus import RamBus
from lib.basic_logger import log


# Create global instance of config
config = Config('/etc/spyspace/mvid_conf.yaml')

# Create global instance of basic transport
host = config.find('redis_host')
queue_size = config.find('redis_queue_size')

db_host = config.find('mysql/mysql_host')
db_user = config.find('mysql/mysql_user')
db_password = config.find('mysql/mysql_passwd')
db_database = config.find('mysql/mysql_database')

ann_path = config.find('ann_path')
ann_max_elements = config.find('ann_max_elements')

vino_mode = config.find('vino_mode')
cpu_extension = config.find('cpu_extension')
detector_model = config.find('intel_fd_model')
landmarks_model = config.find('intel_lm_model')
reid_model = config.find('intel_ri_model')
detection_threshold = config.find('detection_threshold')
pedestrian_model = config.find('intel_pedestrian_model')
pedestrian_threshold = config.find('pedestrian_threshold')

bus = RedisBus(host=host, queue_size=queue_size)
ram_bus = RamBus()

executor = QueryDictExecutor(MySQLEngine, db_host, user=db_user, password=db_password,
                             database=db_database)
features_set = HNSWFeaturesSet(ann_path, ann_max_elements)
frame_handler = OpenVinoHandler(mode=vino_mode, cpu_extension=cpu_extension,
                                detection_threshold=detection_threshold,
                                classDetector=FaceDetectorModel, detector_model=detector_model,
                                classLandmarks=LandmarksDetector, landmarks_model=landmarks_model,
                                classReid=FaceReidModel, reid_model=reid_model)

pedestrian_frame_handler = OpenVinoHandler(mode=vino_mode, cpu_extension=cpu_extension,
                                           detection_threshold=pedestrian_threshold,
                                           classDetector=FaceDetectorModel,
                                           detector_model=pedestrian_model)

