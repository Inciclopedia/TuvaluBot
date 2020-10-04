from typing import Generator

from mwclient import LoginError
from mwclient.page import Page

from common.principal import Principal
from common.tarea import Tarea
from scripts.listaarticulos.constructor_querys import ConstructorQuerys

NAME = "Pon un título a tu script"
DESCRIPTION = "Este script borra redirecciones dobles"
PLANTILLA = "{{InciNuremberg}}"

class PonerPlantilla(Tarea):

    def __init__(self):
        super().__init__()

    def procesar(self, articulo):
        page = Page(self.cliente, articulo)
        token = self.cliente.api("query", meta="tokens", type="csrf")["query"]["tokens"]["csrftoken"]
        self.cliente.api("protect", title=articulo, protections="edit=sysop|move=sysop", reason="Protegido por violación de Términos de Uso", token=token)
        self.logger.info("Procesado " + articulo)

    def obtener_lista_tareas(self) -> Generator[str, None, None]:
        if self.tareas == "":
            constructor = ConstructorQuerys(self.cliente, NAME)
            query = constructor.invocar()
            for page in query.invocar():
                yield page
        else:
            try:
                with open(self.tareas, "r", encoding='utf-8') as f:
                    for tarea in f.read().split('\n'):
                        yield tarea
            except Exception as e:
                print("Hubo un error al leer el archivo")

    def tarea(self):
        for tarea in self.obtener_lista_tareas():
            try:
                self.cliente.login(self.cliente.username, self.password)
            except LoginError:
                pass
            try:
                self.procesar(tarea)
            except Exception as e:
                self.logger.error(str(e))
        self.logger.info("Tarea completada")


Principal(DESCRIPTION).iniciar(PonerPlantilla())
