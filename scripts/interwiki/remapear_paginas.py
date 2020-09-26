from mwclient import Site
from mwclient.page import Page
import json
import sys
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

    def tarea(self):
        if self.tareas == "":
            self.logger.error("Necesito un nombre de archivo de tareas")
            sys.exit(2)
        try:
            with open(self.tareas, "r", encoding='utf-8') as f:
                for tarea in f.readlines():
                    try:
                        self.remapear_pagina(tarea)
                    except Exception as e:
                        self.logger.error(str(e))
        except Exception:
            print("Hubo un error al leer el archivo")


Principal(DESCRIPTION).iniciar(Plantilla())
