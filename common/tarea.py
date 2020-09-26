from abc import ABC, abstractmethod
from logging import Logger
from mwclient import Site


class Tarea(ABC):

    def __init__(self):
        self.cliente: Site = None
        self.logger: Logger = None
        self.tareas = ""

    @abstractmethod
    def tarea(self):
        raise

    def bootstrap(self, cliente: Site, logger: Logger, tareas: str):
        self.cliente = cliente
        self.logger = logger
        self.tareas = tareas

    def run(self):
        if self.cliente is None or self.logger is None:
            raise BootstrapError()
        self.tarea()


class BootstrapError(RuntimeError):
    pass
