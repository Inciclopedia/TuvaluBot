import os

from common.principal import Principal
from common.tarea import Tarea
from scripts.listaarticulos.constructor_querys import ConstructorQuerys

DESCRIPTION = "Pon una descripción bonita de tu tarea aquí"


# Cambia el nombre de Plantilla al de tu tarea... Cambialo abajo también
class ListaArticulos(Tarea):

    def tarea(self):
        constructor = ConstructorQuerys(self.cliente)
        while True:
            query = constructor.invocar()
            correct = input("Confirma que la consulta es correcta? (s/n)")
            if correct == 's':
                archivo = input("Introduzca la ruta donde guardar el archivo con el listado:")
                with open(archivo, "w", encoding="utf-8") as f:
                    for page in query.invocar():
                        f.write(page + os.linesep)
                        print("Se ha generado el listado en " + archivo)
                        return


# No borres esta línea o tu script no iniciará:
Principal(DESCRIPTION).iniciar(ListaArticulos())
