from common.principal import Principal
from common.tarea import Tarea
from scripts.listaarticulos.constructor_querys import ConstructorQuerys

DESCRIPTION = "Genera listados de artículos. Interactivo"


# Cambia el nombre de Plantilla al de tu tarea... Cambialo abajo también
class ListaArticulos(Tarea):

    def tarea(self):
        constructor = ConstructorQuerys(self.cliente, "Consultar lista de artículos")
        query = constructor.invocar()
        archivo = input("Introduzca la ruta donde guardar el archivo con el listado: ")
        with open(archivo, "w", encoding="utf-8") as f:
            for page in query.invocar():
                f.write(page + "\n")
        print("Se ha generado el listado en " + archivo)


# No borres esta línea o tu script no iniciará:
Principal(DESCRIPTION).iniciar(ListaArticulos())
