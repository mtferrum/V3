import redis
import time
from lib.basic_logger import log


client = redis.StrictRedis(host='192.168.2.150', port=6379, db=0)
topic = '/pack_batches'


while True:
    try:
        log.warning('{} topic len = {}'.format(topic, client.llen(topic)))
    except redis.RedisError as e:
        log.critical('{} topic failed with error {}'.format(topic, e))
    time.sleep(60)

