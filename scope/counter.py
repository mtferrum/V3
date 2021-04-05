from lib.iou import IouBoxTracker as Tracker
from lib.mysql_driver import MySQLEngine
from lib.query_executor import QueryDictExecutor
from lib.queries import mysql_queries as queries
from lib.yaml_config import YamlConfig as Config
from lib.basic_logger import log


config = Config('/etc/spyspace/mvid_conf.yaml')

tracker_threshold = config.find('counter/tracker_threshold')
tracker_lag = config.find('counter/tracker_lag')

db_host = config.find('mysql/mysql_host')
db_user = config.find('mysql/mysql_user')
db_password = config.find('mysql/mysql_passwd')
db_database = config.find('mysql/mysql_database')
db_port = config.find('mysql/mysql_port')
db_max_port_size = config.find('mysql/mysql_max_block_size')

tracker = Tracker(tracker_threshold, tracker_lag)
executor = QueryDictExecutor(MySQLEngine, db_host, user=db_user,
                             password=db_password, database=db_database,
                             max_block_size=db_max_port_size)
