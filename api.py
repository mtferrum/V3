from component.http_api import *

if __name__ == "__main__":
    try:
        app.run()
    except Exception as e:
        log.critical('system APPLICATION CLOSED WITH ERROR {}'.format(e))
        sys.exit(1)