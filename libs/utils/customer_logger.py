import inspect
import logging
import os
import sys

from colorama import Fore, Style

IS_LOGGER_SETUP = False

LEVEL_COLORS = {
    'DEBUG': Fore.CYAN,
    'INFO': Fore.GREEN,
    'WARNING': Fore.YELLOW,
    'ERROR': Fore.RED,
    'CRITICAL': Fore.RED + Style.BRIGHT,
}


class ColoredFormatter(logging.Formatter):
    def __init__(self, *args, **kwargs):
        self.use_color = kwargs.pop('use_color', True)
        logging.Formatter.__init__(self, *args, **kwargs)

    def format(self, record):
        levelname = record.levelname
        if not hasattr(record, 'use_color'):
            record.use_color = True
        if self.use_color and record.use_color:
            if not hasattr(record, 'level_color'):
                record.level_color = LEVEL_COLORS[levelname]
            if not hasattr(record, 'color'):
                record.color = LEVEL_COLORS[levelname]
            record.cyan = Fore.CYAN
            record.green = Fore.GREEN
            record.yellow = Fore.YELLOW
            record.red = Fore.RED
            record.blue = Fore.BLUE
            record.magenta = Fore.MAGENTA
        else:
            record.level_color = ''
            record.color = ''
            record.cyan = ''
            record.green = ''
            record.yellow = ''
            record.red = ''
            record.blue = ''
            record.magenta = ''
        msg = super().format(record)
        if self.use_color and record.use_color:
            return f"{msg}{Style.RESET_ALL}"
        return msg


class CustomLogger:
    logger = None

    @staticmethod
    def setup_logger(name=None, format=None, level=None, use_color=True):
        global IS_LOGGER_SETUP
        if not IS_LOGGER_SETUP:
            if level is None:
                level = logging.INFO
            # You can turn on debug with --debug=1 in args
            aruba_debug_env = os.getenv('ARUBA_AUTOMATION_ARUBA_DEBUG', '0').lower()
            for arg in sys.argv:
                if ('debug=1' in arg.lower()
                        or aruba_debug_env == 'true' or aruba_debug_env == '1'):
                    level = logging.DEBUG
                    break

            handler = logging.StreamHandler()
            handler.setLevel(level)
            if format is None:
                # format = '%(asctime)s.%(msecs)03d %(level_color)s%(levelname)-8s %(color)s%(message)s',
                format = '%(asctime)s.%(msecs)03d %(color)s%(message)s'
            formatter = ColoredFormatter(
                fmt=format,
                datefmt='%H:%M:%S',
                use_color=use_color
            )
            handler.setFormatter(formatter)
            if name is None:
                name = ''  # root logger
            CustomLogger.logger = logging.getLogger(name)
            CustomLogger.logger.setLevel(level)
            CustomLogger.logger.addHandler(handler)

            IS_LOGGER_SETUP = True
        return CustomLogger.logger

    @staticmethod
    def printStep(msg, use_color=True):
        CustomLogger.logger.info(msg, extra={'use_color': use_color})

    @staticmethod
    def printStepWithNewLine(msg, use_color=True):
        CustomLogger.logger.info('')
        CustomLogger.logger.info(msg, extra={'use_color': use_color})

    @staticmethod
    def printStart(use_color=True):
        CustomLogger.logger.info('')
        CustomLogger.logger.info('TestCase: {}'.format(inspect.stack()[1][3]),
                                 extra={'use_color': use_color, 'color': Fore.BLUE})

    @staticmethod
    def printGlobalMsg(msg, use_color=True):
        CustomLogger.logger.info('')
        CustomLogger.logger.info(msg, extra={'use_color': use_color, 'color': Fore.BLUE})

    @staticmethod
    def printLog(msg, use_color=True):
        CustomLogger.logger.info(msg, extra={'use_color': use_color, 'color': Fore.MAGENTA})

    @staticmethod
    def printDebug(msg, use_color=True, error=False, quiet=False):
        if not quiet:
            if error:
                CustomLogger.logger.info(msg, extra={'use_color': use_color, 'color': LEVEL_COLORS['ERROR']})
            else:
                CustomLogger.logger.info(msg, extra={'use_color': use_color, 'color': LEVEL_COLORS['DEBUG']})
