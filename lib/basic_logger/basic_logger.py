import logging
import logging.config
import yaml
from yaml import Loader
from sys import argv
import os


try:
    version = open('/'.join(argv[0].split('/')[:-2]) + '/version.txt', 'r').read().replace('\n', '')
except FileNotFoundError:
    version = 'DEV'
# Get logging config from yaml conf file
conf_file = os.environ.get('SPYSPACELOGCONF', '/etc/spyspace/logging_config.yaml')
if not os.path.isfile(conf_file):
    conf_file = '/opt/projects/mvid/lib/basic_logger/config/logging_config.yaml'  # todo: test_config
logging_config_stream = open(conf_file, 'r', encoding='utf8')
logging_config = yaml.load(logging_config_stream, Loader=Loader)
# Add initiator file name to log string template
logging_config['formatters']['simple']['format'] = \
    logging_config['formatters']['simple']['format'].format(
    initiator=argv[0].split('/')[-1], version=version)
logging.config.dictConfig(logging_config)

log = logging.getLogger('spyspace')
log.info('logger started with config {}'.format(conf_file))
