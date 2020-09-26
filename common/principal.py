# Runner principal de tareas del bot
from logging import Logger

from mwclient import Site, MaximumRetriesExceeded, LoginError, APIError
from common.tarea import Tarea
import logging

URL = 'inciclopedia.org'
DEBUG = False

class Principal(object):

    def __init__(self, description):
        self.description = description

    def __parse_args(self):
        import argparse
        parser = argparse.ArgumentParser(description=self.description)
        parser.add_argument('usuario', type=str,
                            help='Nombre de usuario de Inciclopedia')
        parser.add_argument('password', type=str, help='Password de Inciclopedia')
        args = parser.parse_args()
        return args

    def __init_logger(self) -> Logger:
        logging.basicConfig(format='[%(asctime)s] %(message)s')
        return logging.getLogger()

    def iniciar(self, tarea: Tarea):
        import sys
        import inspect
        args = self.__parse_args()
        logger = self.__init_logger()
        logger.setLevel(logging.INFO if not DEBUG else logging.DEBUG)
        logger.info("Iniciando TuvaluBot")
        cliente = Site(URL)
        logger.info("Conectado a Inciclopedia, iniciando sesión")
        try:
            cliente.login(args.usuario, args.password)
            logger.info("Sesión iniciada como " + args.usuario)
        except LoginError:
            logger.error("Login error, las credenciales no son válidas. Cerrando")
            sys.exit(2)
        except MaximumRetriesExceeded:
            logger.error("Login error, máximo de reintentos. Parece que estamos limitados. Cerrando")
            sys.exit(2)
        except APIError:
            logger.error("Login error, error interno. ¿Está funcionando Inci?")
            sys.exit(2)

        # Triple backflip de reflection para obtener automágicamente la primera clase definida
        tarea.bootstrap(cliente, logger)
        tarea.run()
