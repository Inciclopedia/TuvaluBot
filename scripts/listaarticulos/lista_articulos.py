from common.botmain import BotMain
from common.job import Job
from scripts.listaarticulos.constructor_querys import ConstructorQuerys

DESCRIPTION = "Genera listados de artículos. Interactivo"


# Cambia el nombre de Plantilla al de tu tarea... Cambialo abajo también
class ListaArticulos(Job):

    def tarea(self):
        constructor = ConstructorQuerys(self.client, "Consultar lista de artículos")
        query = constructor.invocar()
        archivo = input("Introduzca la ruta donde guardar el archivo con el listado: ")
        with open(archivo, "w", encoding="utf-8") as f:
            for page in query.invocar():
                f.write(page + "\n")
        print("Se ha generado el listado en " + archivo)


# No borres esta línea o tu script no iniciará:
BotMain(DESCRIPTION).start(ListaArticulos())
