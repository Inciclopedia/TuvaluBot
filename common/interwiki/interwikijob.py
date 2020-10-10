from abc import ABC, abstractmethod

import inject
from mwclient.page import Page

from common.interwiki.interwikitask import InterwikiTask
from common.interwiki.strategies.namematch_strategy import InterwikiNameMatchStrategy
from common.interwiki.strategies.translation_strategy import InterwikiTranslationStrategy
from common.interwiki.strategies.wikipedia_strategy import InterwikiWikipediaStrategy
from common.job import Job
from domain.interwiki import Interwiki
from util.config import Config

STRATEGIES = [InterwikiNameMatchStrategy, InterwikiWikipediaStrategy, InterwikiTranslationStrategy]


class InterwikiJob(Job, ABC):

    @abstractmethod
    def __init__(self):
        super().__init__()
        self.interwikis = None
        self.strategies = None

    @inject.param('config', Config)
    def bootstrap(self, config: Config = None):
        self.interwikis = []
        for language, info in config.interwikis:
            self.interwikis.append(Interwiki(language, info["api"], info["fake"], info["skip"]))
        self.strategies = []
        for strategy in STRATEGIES:
            self.strategies.append(strategy(self.client))

    def remapear_pagina(self, nombre):
        if not self.interwikis:
            raise ValueError("call bootstrap first!")
        pagina = Page(self.client, nombre)
        if pagina.redirect:
            return self.remapear_pagina(pagina.resolve_redirect().name)
        self.logger.info("Remapeando página " + nombre + "...")
        tarea = InterwikiTask(pagina, self.client, self.interwikis, self.logger)
        tarea.limpiar_interwikis_rotos()
        faltan = list(tarea.interwikis_faltantes())
        for idioma in faltan:
            self.logger.debug("Buscando artículo en " + idioma)
            for estrategia in self.strategies:
                self.logger.debug("Probando estrategia " + estrategia.get_name())
                resultado = estrategia.run(tarea, idioma)
                if resultado is not None:
                    break
        tarea.guardar_cambios()
