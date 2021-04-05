# Basic scope for NUC
from lib.yaml_config import YamlConfig as Config
from lib.redis_bus import RedisBus
from lib.ping import Ping
from lib.mysql_driver.mysql_engine import MySQLEngine
from lib.query_executor.query_executor import QueryDictExecutor
from lib.queries.mysql_queries import mysql_queries as queries
from lib.basic_logger import log


# Create global instance of config
config = Config('/etc/spyspace/mvid_conf.yaml')

db_host = config.find('mysql/mysql_host')
db_user = config.find('mysql/mysql_user')
db_password = config.find('mysql/mysql_passwd')
db_database = config.find('mysql/mysql_database')

# Create global instance of basic transport
bus = RedisBus(host=config.find('redis_host'))
bus2 = RedisBus(host=config.find('redis_host2'))

ping = Ping(bus, period=18000)

executor = QueryDictExecutor(MySQLEngine, db_host, user=db_user, password=db_password)
executor.execute_query(queries, 'use_mvideo_db')
