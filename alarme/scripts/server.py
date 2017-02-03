import asyncio
import signal

import configargparse
from structlog import get_logger

from alarme import Application
from alarme.scripts.common import init_logging, uncaught_exception, loop_uncaught_exception


def exit_handler(app, logger, sig):
    logger.info('application_signal', name=sig.name, value=sig.value)
    app.stop()


def run(config_path, log,
        core_application_factory=Application,
        ):
    # Logging init
    logger = get_logger()
    loop = asyncio.get_event_loop()
    init_logging(log, 'server')
    loop.set_exception_handler(loop_uncaught_exception)

    # Core init
    logger.info('application_init')
    core_app = core_application_factory(exception_handler=uncaught_exception)
    loop.run_until_complete(core_app.load_config(config_path))

    for signal_code in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(signal_code, exit_handler, core_app, logger, signal_code)

    loop.run_until_complete(core_app.run())
    loop.close()


def main():
    parser = configargparse.ArgParser(description='Alarm system software for Raspberry Pi')
    parser.add_argument('-gc', '--generic-config', is_config_file=True, help='Generic config')
    parser.add_argument('-c', '--config', help='Main config')
    parser.add_argument('-l', '--log', type=str, default='/var/log/alarme', help='Logs dir')
    args = parser.parse_args()
    run(args.config, args.log)


if __name__ == '__main__':
    main()
