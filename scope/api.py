from lib.basic_logger import log
from lib.yaml_config import YamlConfig as Config
from lib.redis_bus import RedisBus #NB! Import before MySQLEngine to avoid SegmentationFault
from lib.query_executor.query_executor import QueryDictExecutor
from lib.mysql_driver.mysql_engine import MySQLEngine
from lib.queries.mysql_queries import mysql_queries as query
from lib.get_face_hash import Infer
from lib.hnsw_features_set import HNSWFeaturesSet
from mysql.connector.errors import ProgrammingError, InterfaceError, OperationalError, IntegrityError


# Create global instance of config
project_dir = "/opt/projects/mvid"
#project_dir = "/home/tech/PycharmProjects/mvid"
config = Config('/etc/spyspace/mvid_conf.yaml')
# Create global instance of basic transport
bus = RedisBus(host=config.find('redis_host'))
executor = QueryDictExecutor(MySQLEngine, config.find('mysql_host'),
                         user=config.find('mysql_user'),
                         password=config.find('mysql_passwd'),
                         database="mvideo")
infer = Infer()
features_set = HNSWFeaturesSet(config.find('ann_path'), config.find('ann_max_elements'))
