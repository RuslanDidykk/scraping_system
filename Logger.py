# coding: utf-8

import logging


class Logger(object):
    LOG_FORMATTER = '%(asctime)s - %(levelname)-10s  -  %(message)s'


    def __init__(self, name='logger', level=logging.DEBUG):
        self.formatter = logging.Formatter(self.LOG_FORMATTER)

        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        fh = logging.FileHandler('logs/%s.log' % name, 'a')
        self.logger.addHandler(fh)
        fh.setFormatter(self.formatter)


        sh = logging.StreamHandler()
        self.logger.addHandler(sh)
        sh.setFormatter(self.formatter)

    def debug(self, msg):
        self.logger.debug(msg)

    def info(self, msg):
        self.logger.info(msg)

    def warning(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.error(msg)

def test():
    log.debug("debuG")

if __name__ == '__main__':
    log = Logger()
    test()
    log.debug('debug1')
    log.info('info1')
    log.warning('warning1')
    log.error('error1')