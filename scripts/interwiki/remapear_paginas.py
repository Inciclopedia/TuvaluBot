from mwclient import Site
from common.tarea import Tarea
from common.principal import Principal

DESCRIPTION = "Pon una descripción bonita de tu tarea aquí"


class Plantilla(Tarea):

    def tarea(self):
        # Aquí va tu código. Puedes acceder al cliente con self.client.
        self.logger.info("todo ok")


Principal(DESCRIPTION).iniciar(Plantilla())
