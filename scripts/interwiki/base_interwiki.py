import json
from abc import ABC, abstractmethod

from mwclient.page import Page

from common.tarea import Tarea
from scripts.interwiki.estrategias.estrategia_nombredirecto import EstrategiaNombreDirecto
from scripts.interwiki.estrategias.estrategia_traduccion import EstrategiaTraduccion
from scripts.interwiki.estrategias.estrategia_wikipedia import EstrategiaWikipedia
from scripts.interwiki.interwiki import Interwiki
from scripts.interwiki.tareainterwiki import TareaInterwiki

ESTRATEGIAS = [EstrategiaNombreDirecto, EstrategiaWikipedia, EstrategiaTraduccion]


class BaseInterwiki(Tarea, ABC):

    @abstractmethod
    def __init__(self):
        super().__init__()
        self.interwikis = []
        with open("scripts/interwiki/interwiki.json", "r") as f:
            iws = json.load(f)
            for idioma, info in iws.items():
                self.interwikis.append(Interwiki(idioma, info["api"], info["fake"], info["skip"]))
        self.estrategias = []
        for estrategia in ESTRATEGIAS:
            self.estrategias.append(estrategia(self.cliente))

    def remapear_pagina(self, nombre):
        pagina = Page(self.cliente, nombre)
        if pagina.redirect:
            return self.remapear_pagina(pagina.resolve_redirect().name)
        self.logger.info("Remapeando página " + nombre + "...")
        tarea = TareaInterwiki(pagina, self.cliente, self.interwikis, self.logger)
        tarea.limpiar_interwikis_rotos()
        faltan = list(tarea.interwikis_faltantes())
        for idioma in faltan:
            self.logger.debug("Buscando artículo en " + idioma)
            for estrategia in self.estrategias:
                self.logger.debug("Probando estrategia " + estrategia.get_name())
                resultado = estrategia.ejecutar(tarea, idioma)
                if resultado is not None:
                    break
        tarea.guardar_cambios()
