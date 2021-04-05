from component.face_listener import *

if __name__ == "__main__":
    try:
        bus.listen()
    except Exception as e:
        log.exception(e)
        log.critical('system APPLICATION CLOSED WITH ERROR {}'.format(e))
        sys.exit(1)
    log.info('system APPLICATION FINISHED')
