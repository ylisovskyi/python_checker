from logging import Logger, DEBUG, NOTSET
from datetime import datetime


class LoggerProxy(Logger):

    logger = Logger('default')

    @staticmethod
    def getLogger(name, debug=False):
        level = DEBUG if debug else NOTSET
        LoggerProxy.logger = Logger(name, level)
        return LoggerProxy.logger

    @staticmethod
    def write_to_file(msg, level):
        now = datetime.now()
        with open('logs.log', 'a') as f:
            f.write(f'{LoggerProxy.logger.name}: {now} - {level} - {msg}\n')

    @staticmethod
    def info(msg, *args, **kwargs):
        LoggerProxy.write_to_file(msg, 'INFO')
        LoggerProxy.logger.info(msg, *args, **kwargs)

    @staticmethod
    def debug(msg, *args, **kwargs):
        LoggerProxy.write_to_file(msg, 'DEBUG')
        Logger.debug(msg, *args, **kwargs)

    @staticmethod
    def error(msg, *args, **kwargs):
        LoggerProxy.write_to_file(msg, 'ERROR')
        Logger.error(msg, *args, **kwargs)


