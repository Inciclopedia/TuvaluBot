from logging import Logger
from typing import List
from urllib.parse import quote

from mwclient import Site
from mwclient.page import Page
import requests

from scripts.interwiki.interwiki import Interwiki


class TareaInterwiki(object):

    def __init__(self, pagina: Page, cliente: Site, interwikis: List[Interwiki], logger: Logger):
        self.pagina = pagina
        self.cliente = cliente
        self.enlaces_interwiki = list(pagina.langlinks())
        self.interwikis = interwikis
        self.logger = logger
        self.editado = False
        self.texto = self.pagina.text()
        self.creados = []
        self.borrados = []

    def existe_interwiki(self, idioma):
        return len(list(filter(lambda iw: iw[0] == idioma, self.enlaces_interwiki))) > 0

    def __recuperar_interwiki(self, idioma):
        for iw in self.interwikis:
            if iw.idioma == idioma:
                return iw
        return None

    def obtener_link_interwiki(self, idioma, articulo):
        interwiki = self.__recuperar_interwiki(idioma)
        es_fake = interwiki is not None and interwiki.fake
        if es_fake:
            link_interwiki = "{{" + idioma + "|" + articulo + "}}"
        else:
            link_interwiki = "[[" + idioma + ":" + articulo + "]]"
        return link_interwiki

    def borrar_interwiki(self, idioma, razon, articulo):
        self.logger.info("Eliminando interwiki %s [%s] %s -> %s", razon, idioma, self.pagina.name, articulo)
        self.editado = True
        self.texto = self.texto.replace(self.obtener_link_interwiki(idioma, articulo), "")
        self.borrados.append(idioma)

    def crear_interwiki(self, idioma, articulo):
        self.logger.info("Creando interwiki [%s] %s -> %s", idioma, self.pagina.name, articulo)
        self.editado = True
        self.texto = self.texto + "\n" + self.obtener_link_interwiki(idioma, articulo)
        self.creados.append(idioma)

    def buscar_articulo_en_interwiki(self, idioma, articulo, existia_antes=False):
        interwiki = self.__recuperar_interwiki(idioma)
        if interwiki.skip:
            return None
        if interwiki is None:
            self.logger.debug("Interwiki obsoleta [%s] %s -> %s", idioma, self.pagina.name, articulo)
            self.borrar_interwiki(idioma, "obsoleta", articulo)
            return None
        url = "http://" + interwiki.api + "/wiki/" + quote(articulo)
        try:
            respuesta = requests.get(url)
        except:
            # algún error de requests, no tocaremos nada...
            return articulo if existia_antes else None
        if respuesta.status_code == 404:
            if existia_antes:
                self.logger.debug("Interwiki no encontrada [%s] %s -> %s", idioma, self.pagina.name, articulo)
                self.borrar_interwiki(idioma, "no encontrada", articulo)
                return None
            else:
                self.logger.debug("Interwiki no encontrada [%s] %s -> %s", idioma, self.pagina.name, articulo)
                return None
        else:
            self.logger.debug("Interwiki encontrada [%s] %s -> %s", idioma, self.pagina.name, articulo)
            if not existia_antes:
                self.crear_interwiki(idioma, articulo)
            return articulo

    def interwikis_faltantes(self):
        faltan = []
        for interwiki in self.interwikis:
            found = False
            for idioma, articulo in self.enlaces_interwiki:
                if interwiki.idioma == idioma:
                    found = True
                    break
            if not found:
                faltan.append(interwiki.idioma)
        return faltan

    def limpiar_interwikis_rotos(self):
        self.logger.debug("Limpiando artículo %s", self.pagina.name)
        for idioma, articulo in self.enlaces_interwiki:
            self.buscar_articulo_en_interwiki(idioma, articulo, existia_antes=True)

    def generar_sumario(self):
        sumario = "interwiki: "
        if len(self.creados) > 0:
            sumario = sumario + "añadidos " + ", ".join(self.creados) + ("; " if len(self.borrados) > 0 else "")
        if len(self.borrados) > 0:
            sumario = sumario + "borrados " + ", ".join(self.borrados)
        return sumario

    def guardar_cambios(self):
        if self.editado:
            self.logger.info("Guardando artículo actualizado %s", self.pagina.name)
            self.pagina.edit(self.texto, summary=self.generar_sumario())
            self.creados = []
            self.borrados = []
            self.editado = False
            self.pagina = Page(self.pagina.site, self.pagina.name)
            self.texto = self.pagina.text()
            self.enlaces_interwiki = list(self.pagina.langlinks())
