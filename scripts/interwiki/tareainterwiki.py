from logging import Logger
from typing import List
from urllib.parse import quote

from mwclient import Site
from mwclient.page import Page
import requests

from scripts.interwiki.interwiki import Interwiki
import re


class TareaInterwiki(object):

    def __init__(self, pagina: Page, cliente: Site, interwikis: List[Interwiki], logger: Logger):
        self.pagina = pagina
        self.texto = self.pagina.text()
        self.cliente = cliente
        self.enlaces_interwiki = dict()
        for idioma, link in pagina.langlinks():
            if idioma not in self.enlaces_interwiki:
                self.enlaces_interwiki[idioma] = [link]
            else:
                self.enlaces_interwiki[idioma].append(link)
        self.interwikis = interwikis
        self.logger = logger
        self.editado = False
        self.creados = []
        self.borrados = []
        self.ordenados = False

    def existe_interwiki(self, idioma):
        return idioma in self.enlaces_interwiki

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
        if idioma in self.enlaces_interwiki:
            del self.enlaces_interwiki[idioma]

    def crear_interwiki(self, idioma, articulo):
        self.logger.info("Creando interwiki [%s] %s -> %s", idioma, self.pagina.name, articulo)
        self.editado = True
        self.texto = self.texto + "\n" + self.obtener_link_interwiki(idioma, articulo)
        self.creados.append(idioma)

    def buscar_articulo_en_interwiki(self, idioma, articulo, existia_antes=False):
        interwiki = self.__recuperar_interwiki(idioma)
        if interwiki is not None and interwiki.skip:
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
            if not interwiki.fake:
                if interwiki.idioma in self.enlaces_interwiki:
                    found = True
            else:
                if re.search(r"{{" + interwiki.idioma + r"\|[^}]+(?:}){2}\n", self.texto) is not None:
                    found = True
            if not found:
                faltan.append(interwiki.idioma)
        return faltan

    def limpiar_interwikis_rotos(self):
        self.logger.debug("Limpiando artículo %s", self.pagina.name)
        for idioma, articulos in self.enlaces_interwiki.items():
            for articulo in articulos:
                self.buscar_articulo_en_interwiki(idioma, articulo, existia_antes=True)

    def generar_sumario(self):
        tareas_hechas = []
        if len(self.creados) > 0:
            tareas_hechas.append("añadidos " + ", ".join(self.creados))
        if len(self.borrados) > 0:
            tareas_hechas.append("borrados " + ", ".join(self.borrados))
        if self.ordenados:
            tareas_hechas.append("ordenados interwikis")
        return "mant. interwiki: " + "; ".join(tareas_hechas)

    def ordenar_interwikis(self):
        resultados = re.findall(r"(?:\[|{){2}[^:\]}]+(?:|\|)[^\]}]+(?:\]|}){2}\n", self.texto)
        interwikis = dict()
        for interwiki in resultados:
            interwiki.replace('{', '').replace('}', '').replace('[', '').replace(']', '')
            if ':' in interwiki:
                idioma = interwiki[2:interwiki.index(':')]
                if self.__recuperar_interwiki(idioma) is not None:
                    interwikis[idioma] = interwiki
            elif '|' in interwiki:
                idioma = interwiki[2:interwiki.index('|')]
                if self.__recuperar_interwiki(idioma) is not None:
                    interwikis[idioma] = interwiki
        antes = interwikis.keys()
        despues = sorted(antes, key=str.casefold)
        if antes != despues:
            self.editado = True
            self.ordenados = True
            for interwiki in interwikis.values():
                # borramos todas las interwikis encontradas para recrear la lista
                self.texto = self.texto.replace(interwiki, "")
            self.texto = self.texto + "\n"
            for idioma in despues:
                self.texto = self.texto + interwikis[idioma]

    def guardar_cambios(self):
        self.ordenar_interwikis()
        if self.editado:
            self.logger.info("Guardando artículo actualizado %s", self.pagina.name)
            self.pagina.edit(self.texto, summary=self.generar_sumario())
            self.creados = []
            self.borrados = []
            self.editado = False
            self.ordenados = False
            self.pagina = Page(self.pagina.site, self.pagina.name)
            self.texto = self.pagina.text()
            self.enlaces_interwiki = dict()
            for idioma, link in self.pagina.langlinks():
                if idioma not in self.enlaces_interwiki:
                    self.enlaces_interwiki[idioma] = [link]
                else:
                    self.enlaces_interwiki[idioma].append(link)
