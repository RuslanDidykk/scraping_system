import logging


class Logger():

    def __init__(self, file_name):
        logging.basicConfig(format=u'%(levelname)-8s [%(asctime)s] %(message)s', level=logging.INFO,
                            filename=file_name + '.log')

    def info(self, msg):
        logging.info(msg=msg)

    def warning(self, msg):
        logging.warning(msg=msg)

    def error(self, msg):
        logging.warning(msg=msg)
