from typing import Generator

import inject
from mwclient import LoginError

from common.botmain import BotMain
from common.interwiki.interwikijob import InterwikiJob
from scripts.listaarticulos.constructor_querys import ConstructorQuerys
from util.lang import Lang

DESCRIPTION = "Este script remapea los interwikis de una página localizando en todos los interwikis"


class InterwikiRemapper(InterwikiJob):

    def __init__(self):
        super().__init__()

    @inject.param('lang', Lang)
    def obtener_lista_tareas(self, lang: Lang = None) -> Generator[str, None, None]:
        if self.task_file == "":
            constructor = ConstructorQuerys(self.client, lang.t("interwiki.querybuilder_title"))
            query = constructor.invocar()
            for page in query.invocar():
                yield page
        else:
            try:
                with open(self.task_file, "r", encoding='utf-8') as f:
                    for tarea in f.read().split('\n'):
                        yield tarea
            except Exception as e:
                print(lang.t("common.ioerror"))

    @inject.param('lang', Lang)
    def tarea(self, lang: Lang = None):
        for tarea in self.obtener_lista_tareas():
            try:
                self.client.login(self.client.username, self.password)
            except LoginError:
                pass
            try:
                self.remapear_pagina(tarea)
            except Exception as e:
                self.logger.error(str(e))
        self.logger.info(lang.t("common.task_completed"))


BotMain(DESCRIPTION).start(InterwikiRemapper())
