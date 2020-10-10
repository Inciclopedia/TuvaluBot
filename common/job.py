from abc import ABC, abstractmethod
from logging import Logger

import inject
from mwclient import Site

from util.configimpl import Config
from util.lang import Lang


class Job(ABC):

    def __init__(self):
        self.client: Site = None
        self.logger: Logger = None
        self.task_file = ""
        self.password = ""
        self.lang = None
        self.config = None

    @abstractmethod
    def task(self):
        raise

    @inject.param('lang', Lang)
    @inject.param('config', Config)
    def bootstrap(self, client: Site, logger: Logger, task_file: str, password: str, lang: Lang = None,
                  config: Config = None):
        self.client = client
        self.logger = logger
        self.task_file = task_file
        self.password = password
        self.lang = lang
        self.config = config

    def run(self):
        if self.client is None or self.logger is None:
            raise BootstrapError()
        self.task()


class BootstrapError(RuntimeError):
    pass
