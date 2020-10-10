from abc import ABC, abstractmethod
from logging import Logger

from mwclient import Site


class Job(ABC):

    def __init__(self):
        self.client: Site = None
        self.logger: Logger = None
        self.task_file = ""
        self.password = ""


    @abstractmethod
    def tarea(self):
        raise

    def bootstrap(self, client: Site, logger: Logger, task_file: str, password: str):
        self.client = client
        self.logger = logger
        self.task_file = task_file
        self.password = password

    def run(self):
        if self.client is None or self.logger is None:
            raise BootstrapError()
        self.tarea()


class BootstrapError(RuntimeError):
    pass
