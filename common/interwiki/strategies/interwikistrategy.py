from abc import ABC, abstractmethod
from typing import Optional

from mwclient import Site

from common.interwiki.interwikitask import InterwikiTask


class InterwikiStrategy(ABC):

    def __init__(self, client: Site):
        self.cliente = client

    @abstractmethod
    def run(self, task: InterwikiTask, language: str) -> Optional[str]:
        raise

    @abstractmethod
    def get_name(self) -> str:
        raise
