import sys
from component.reader import ReaderStreams
from component.ping import ping
from scope import log


if __name__ == '__main__':
    log.info('system APPLICATION STARTING...')
    try:
        ping.add_stage('reader', send=True)
        reader = ReaderStreams()
        log.info('system APPLICATION STARTED')
        reader.run_streams()
    except Exception as e:
        log.exception(e)
        log.critical('system APPLICATION CLOSED WITH ERROR {}'.format(e))
        sys.exit(1)
    log.info('system APPLICATION FINISHED')
