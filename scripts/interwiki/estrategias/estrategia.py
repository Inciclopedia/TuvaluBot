from typing import Union, Optional

from mwclient import Site
from abc import ABC, abstractmethod

from scripts.interwiki.interwiki import Interwiki
from scripts.interwiki.tareainterwiki import TareaInterwiki


class Estrategia(ABC):

    def __init__(self, cliente: Site):
        self.cliente = cliente

    @abstractmethod
    def ejecutar(self, tarea: TareaInterwiki, idioma: str) -> Optional[str]:
        raise

    @abstractmethod
    def get_name(self) -> str:
        raise
