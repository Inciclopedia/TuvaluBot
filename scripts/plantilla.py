from common.botmain import BotMain
from common.job import Job

DESCRIPTION = "Pon una descripción bonita de tu tarea aquí"


# Cambia el nombre de Plantilla al de tu tarea... Cambialo abajo también
class Plantilla(Job):

    def tarea(self):
        # Aquí va tu código. Puedes acceder al cliente con self.client.
        pass


# No borres esta línea o tu script no iniciará:
BotMain(DESCRIPTION).start(Plantilla())
