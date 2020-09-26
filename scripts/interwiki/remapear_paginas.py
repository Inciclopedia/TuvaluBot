from mwclient import Site
from mwclient.page import Page
import json
from common.tarea import Tarea
from common.principal import Principal
from scripts.interwiki.estrategias.estrategia_nombredirecto import EstrategiaNombreDirecto
from scripts.interwiki.estrategias.estrategia_traduccion import EstrategiaTraduccion
from scripts.interwiki.estrategias.estrategia_wikipedia import EstrategiaWikipedia
from scripts.interwiki.interwiki import Interwiki
from scripts.interwiki.tareainterwiki import TareaInterwiki

DESCRIPTION = "Este script remapea los interwikis de una página localizando en todos los interwikis"
ESTRATEGIAS = [EstrategiaNombreDirecto, EstrategiaWikipedia, EstrategiaTraduccion]


class Plantilla(Tarea):

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
        self.logger.info("Remapeando página " + nombre + "...")
        pagina = Page(self.cliente, nombre)
        tarea = TareaInterwiki(pagina, self.cliente, self.interwikis, self.logger)
        tarea.limpiar_interwikis_rotos()
        # Es necesario guardar los cambios ahora para que se busquen los interwikis rotos una vez eliminados.
        tarea.guardar_cambios()
        faltan = list(tarea.interwikis_faltantes())
        for idioma in faltan:
            self.logger.debug("Buscando artículo en " + idioma)
            for estrategia in self.estrategias:
                self.logger.debug("Probando estrategia " + estrategia.get_name())
                resultado = estrategia.ejecutar(tarea, idioma)
                if resultado is not None:
                    break
        tarea.guardar_cambios()


    def tarea(self):
        self.remapear_pagina("Albert Einstein")


Principal(DESCRIPTION).iniciar(Plantilla())
