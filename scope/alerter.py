# Basic scope for NUC Alerter
from lib.redis_bus import RedisBus
from lib.telegram import Telegram, MultiTelegram
from lib.mysql_driver.mysql_engine import MySQLEngine
from lib.query_executor.query_executor import QueryDictExecutor
from lib.yaml_config import YamlConfig as Config
from lib.basic_logger import log


# Create global instance of config
config = Config('/etc/spyspace/mvid_conf.yaml')
# Create global instance of basic transport
redis_host = config.find('redis_host')

proxy = config.find('proxy')
telebot_black_token = config.find('telebot_black_token')
telebot_white_token = config.find('telebot_white_token')
telebot_password = config.find('telebot_password')

db_host = config.find('mysql/mysql_host')
db_user = config.find('mysql/mysql_user')
db_password = config.find('mysql/mysql_passwd')
db_database = config.find('mysql/mysql_database')

bus = RedisBus(host=redis_host)
messenger = MultiTelegram(proxy=proxy, blacklist=telebot_black_token, whitelist=telebot_white_token)
executor = QueryDictExecutor(MySQLEngine, db_host, user=db_user, password=db_password,
                             database=db_database)
