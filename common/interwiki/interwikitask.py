import re
from logging import Logger
from typing import List
from urllib.parse import quote

import requests
from mwclient import Site
from mwclient.page import Page

from domain.interwiki import Interwiki


class InterwikiTask(object):

    def __init__(self, page: Page, client: Site, interwikis: List[Interwiki], logger: Logger):
        self.page = page
        self.texto = self.page.text()
        self.client = client
        self.interwiki_links = dict()
        for language, link in page.langlinks():
            if language not in self.interwiki_links:
                self.interwiki_links[language] = [link]
            else:
                self.interwiki_links[language].append(link)
        self.interwikis = interwikis
        self.logger = logger
        self.edited = False
        self.created = []
        self.deleted = []

    def interwiki_exists(self, idioma):
        return idioma in self.interwiki_links

    def __fetch_interwiki(self, idioma):
        for iw in self.interwikis:
            if iw.idioma == idioma:
                return iw
        return None

    def get_interwiki_wikicode(self, idioma, articulo):
        interwiki = self.__fetch_interwiki(idioma)
        if interwiki is not None and interwiki.fake:
            interwiki_wikicode = "{{" + idioma + "|" + articulo + "}}"
        else:
            interwiki_wikicode = "[[" + idioma + ":" + articulo + "]]"
        return interwiki_wikicode

    def remove_interwiki(self, idioma, razon, articulo):
        self.logger.info("Eliminando interwiki %s [%s] %s -> %s", razon, idioma, self.page.name, articulo)
        self.edited = True
        self.texto = self.texto.replace(self.get_interwiki_wikicode(idioma, articulo), "")
        self.deleted.append(idioma)
        if idioma in self.interwiki_links:
            del self.interwiki_links[idioma]

    def create_interwiki(self, idioma, articulo):
        self.logger.info("Creando interwiki [%s] %s -> %s", idioma, self.page.name, articulo)
        self.edited = True
        self.texto = self.texto + "\n" + self.get_interwiki_wikicode(idioma, articulo)
        self.created.append(idioma)

    def locate_article_on_interwiki(self, idioma, articulo, existia_antes=False):
        interwiki = self.__fetch_interwiki(idioma)
        if interwiki is not None and interwiki.skip:
            return None
        if interwiki is None:
            self.logger.debug("Interwiki obsoleta [%s] %s -> %s", idioma, self.page.name, articulo)
            self.remove_interwiki(idioma, "obsoleta", articulo)
            return None
        url = "http://" + interwiki.api + "/wiki/" + quote(articulo)
        try:
            respuesta = requests.get(url)
        except:
            # algún error de requests, no tocaremos nada...
            return articulo if existia_antes else None
        if respuesta.status_code == 404:
            if existia_antes:
                self.logger.debug("Interwiki no encontrada [%s] %s -> %s", idioma, self.page.name, articulo)
                self.remove_interwiki(idioma, "no encontrada", articulo)
                return None
            else:
                self.logger.debug("Interwiki no encontrada [%s] %s -> %s", idioma, self.page.name, articulo)
                return None
        else:
            self.logger.debug("Interwiki encontrada [%s] %s -> %s", idioma, self.page.name, articulo)
            if not existia_antes:
                self.create_interwiki(idioma, articulo)
            return articulo

    def interwikis_faltantes(self):
        faltan = []
        for interwiki in self.interwikis:
            found = False
            if not interwiki.fake:
                if interwiki.idioma in self.interwiki_links:
                    found = True
            else:
                if re.search(r"{{" + interwiki.idioma + r"\|[^}]+(?:}){2}\n", self.texto) is not None:
                    found = True
            if not found:
                faltan.append(interwiki.idioma)
        return faltan

    def limpiar_interwikis_rotos(self):
        self.logger.debug("Limpiando artículo %s", self.page.name)
        for idioma, articulos in list(self.interwiki_links.items()):
            for articulo in articulos:
                self.locate_article_on_interwiki(idioma, articulo, existia_antes=True)

    def generar_sumario(self):
        tareas_hechas = []
        if len(self.created) > 0:
            tareas_hechas.append("añadidos " + ", ".join(self.created))
        if len(self.deleted) > 0:
            tareas_hechas.append("borrados " + ", ".join(self.deleted))
        return "mant. interwiki: " + "; ".join(tareas_hechas)


    def guardar_cambios(self):
        if self.edited:
            self.logger.info("Guardando artículo actualizado %s", self.page.name)
            self.page.edit(self.texto, summary=self.generar_sumario())
            self.created = []
            self.deleted = []
            self.edited = False
            self.page = Page(self.page.site, self.page.name)
            self.texto = self.page.text()
            self.interwiki_links = dict()
            for idioma, link in self.page.langlinks():
                if idioma not in self.interwiki_links:
                    self.interwiki_links[idioma] = [link]
                else:
                    self.interwiki_links[idioma].append(link)
