import os.path
import sys
import logging.config

import structlog
from structlog import get_logger

from alarme.overrides.logging_extras import ProcessorFormatter, event_dict_to_message


def uncaught_exception(value):
    logger = get_logger()
    try:
        print(value)
        raise value
    except:
        logger.critical('uncaught_exception', name=type(value).__name__, args=value.args, exc_info=True)


def sys_uncaught_exception(exctype, value, tb):
    return uncaught_exception(value)


def loop_uncaught_exception(loop, exc_info):
    exception = exc_info.get('exception')
    if exception:
        return uncaught_exception(exception)


def init_logging(log_dir, name):
    if not os.path.exists(log_dir):
        os.mkdir(log_dir)
    plain_processor = structlog.dev.ConsoleRenderer() # TODO: ConsoleRenderer without coloring
    color_processor = structlog.dev.ConsoleRenderer()
    plain_processor._level_to_color['info'] = structlog.dev.BRIGHT
    color_processor._level_to_color['info'] = structlog.dev.BRIGHT
    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'plain': {
                '()': ProcessorFormatter,
                'processor': plain_processor,
            },
            'colored': {
                '()': ProcessorFormatter,
                'processor': color_processor,
            },
        },
        'handlers': {
            'default': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'colored',
            },
            'file': {
                'level': 'DEBUG',
                'class': 'logging.handlers.WatchedFileHandler',
                'filename': os.path.join(log_dir, '{}.log'.format(name)),
                'formatter': 'plain',
            },
        },
        'loggers': {
            '': {
                'handlers': ['default', 'file'],
                'level': 'DEBUG',
                'propagate': True,
            },
            'asyncio': {
                'propagate': False,
            },
        }
    })
    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt='%Y-%m-%d %H:%M:%S'),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            event_dict_to_message,
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    sys.excepthook = sys_uncaught_exception
