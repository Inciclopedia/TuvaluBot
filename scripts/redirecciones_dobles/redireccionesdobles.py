0
from typing import Generator

from mwclient import LoginError
from mwclient.page import Page

from common.botmain import BotMain
from common.job import Job
from scripts.listaarticulos.constructor_querys import ConstructorQuerys

DESCRIPTION = "Este script borra redirecciones dobles"


class RedireccionesDobles(Job):

    def __init__(self):
        super().__init__()

    def neutralizar_dobles(self, articulo):
        pagina = Page(self.client, articulo)
        if not pagina.redirect:
            return
        self.logger.info("Procesando redirección " + articulo)
        cadena = []
        while pagina.redirect:
            if pagina.name in cadena:
                self.logger.warning("Detectada referencia circular en " + articulo)
                return
            cadena.append(pagina.name)
            pagina = Page(self.client, pagina.redirects_to())
        if len(cadena) > 1:
            for redireccion in cadena[:-1]:
                self.logger.info("Redireción doble encontrada en " + redireccion + ", destino final " + pagina.name +
                                 ", resolviendo")
                redir = Page(self.client, redireccion)
                redir.edit("#REDIRECT [[" + pagina.name + "]]", "Resolviendo doble redirección, redirigiendo a " + pagina.name)


    def obtener_lista_tareas(self) -> Generator[str, None, None]:
        if self.task_file == "":
            constructor = ConstructorQuerys(self.client, "Eliminar Redirecciones Dobles")
            query = constructor.invocar()
            for page in query.invocar():
                yield page
        else:
            try:
                with open(self.task_file, "r", encoding='utf-8') as f:
                    for tarea in f.read().split('\n'):
                        yield tarea
            except Exception as e:
                print("Hubo un error al leer el archivo")

    def tarea(self):
        for tarea in self.obtener_lista_tareas():
            try:
                self.client.login(self.client.username, self.password)
            except LoginError:
                pass
            try:
                self.neutralizar_dobles(tarea)
            except Exception as e:
                self.logger.error(str(e))
        self.logger.info("Tarea completada")


BotMain(DESCRIPTION).start(RedireccionesDobles())
