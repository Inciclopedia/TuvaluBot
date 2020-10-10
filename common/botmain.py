# Runner principal de tareas del bot
import logging
from logging import Logger

import inject
from mwclient import Site, MaximumRetriesExceeded, LoginError, APIError

from common.job import Job
from util.config import IConfig
from util.injector import bind_injector
from util.lang import Lang

URL = 'inciclopedia.org'


class BotMain(object):

    def __init__(self, description):
        self.description = description

    def __init_logger(self) -> Logger:
        logging.basicConfig(format='[%(asctime)s] %(message)s')
        return logging.getLogger()

    @inject.param('config', IConfig)
    @inject.param('lang', Lang)
    def __init_system_phase2(self, config: IConfig = None, lang: Lang = None):
        config.bootstrap(self.description)
        lang.set_lang(config.config["client"]["display_language"])
        logger = self.__init_logger()
        logger.setLevel(logging.INFO if not config.args.debug else logging.DEBUG)
        return config.args, config.config, logger, lang

    def __init_system(self):
        bind_injector()
        return self.__init_system_phase2()

    def start(self, job: Job):
        import sys
        args, config, logger, lang = self.__init_system()
        logger.info(lang.t("main.starting_bot"))
        client = Site(config["wiki"]["api"])
        logger.info(lang.t("main.logging_in").format(name=config["wiki"]["name"]))
        try:
            client.user = args.user
            client.password = args.password
            client.login(args.user, args.password)
            logger.info(lang.t("main.logged_in").format(user=args.user))
        except LoginError:
            logger.error(lang.t("main.wrong_credentials"))
            sys.exit(2)
        except MaximumRetriesExceeded:
            logger.error(lang.t("main.maximum_retries"))
            sys.exit(2)
        except APIError:
            logger.error(lang.t("main.api_error"))
            sys.exit(2)

        job.bootstrap(client, logger, args.tasks, args.password)
        job.run()
