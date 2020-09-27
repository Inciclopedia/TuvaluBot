import os
from enum import Enum
from typing import List, Union, Optional, Iterable

from mwclient import Site

from domain.namespace import Namespace
from domain.query_articulos import QueryArticulos
from util.siteinfo import SiteInfo


def limpiar():
    os.system('cls' if os.name == 'nt' else 'clear')


class Tipo(Enum):
    CADENA = 1
    ENTERO = 2
    SELECTOR = 3
    SELECTOR_MULTIPLE_PIPE = 4
    BOOLEAN = 5
    SELECTOR_MULTIPLE_LISTA = 6


class Opcion(object):

    def __init__(self, display, id):
        self.display = display
        self.id = id


def generar_opciones_ns(namespaces: Iterable[Namespace]):
    lista = []
    for namespace in namespaces:
        lista.append(Opcion(namespace.site_name, namespace.id))
    return lista


class Condicion(object):

    def __init__(self, tecla, nombre, propiedad, tipo=Tipo.CADENA, valor=None, opciones: List[Opcion]=None, depende_de=None):
        self.tecla = tecla
        self.nombre = nombre
        self.tipo = tipo
        self.valor: Union[str, int, Opcion, bool, List[Opcion]] = valor
        self.propiedad = propiedad
        self.opciones = opciones
        self.depende_de = depende_de

    def pintar(self, query: QueryArticulos):
        if self.depende_de is not None and getattr(query, self.depende_de) == False:
            return
        if self.tipo == Tipo.CADENA:
            print("%s - %s: [%.40s]" % (self.tecla, self.nombre, self.valor or "", ))
        elif self.tipo == Tipo.ENTERO:
            print("%s - %s: [%.40s]" % (self.tecla, self.nombre, str(self.valor) if self.valor is not None else "", ))
        elif self.tipo == Tipo.SELECTOR:
            print("%s - %s: [%.40s]" % (self.tecla, self.nombre, self.valor.display))
        elif self.tipo == Tipo.SELECTOR_MULTIPLE_PIPE or self.tipo == Tipo.SELECTOR_MULTIPLE_LISTA:
            disp = []
            for opcion in self.valor:
                for opt in self.opciones:
                    if opcion.id == opt.id:
                        disp.append(opcion.display)
            print("%s - %s: [%.40s]" % (self.tecla, self.nombre, ", ".join(disp), ))
        elif self.tipo == Tipo.BOOLEAN:
            print("%s - [%s] %s" % (self.tecla, "X" if self.valor else " ", self.nombre))

    def preguntar(self, query: QueryArticulos):
        limpiar()
        if self.tipo == Tipo.CADENA:
            self.__preguntar_cadena()
            setattr(query, self.propiedad, self.valor)
        elif self.tipo == Tipo.ENTERO:
            self.__preguntar_entero()
            setattr(query, self.propiedad, self.valor)
        elif self.tipo == Tipo.BOOLEAN:
            self.valor = not self.valor
            setattr(query, self.propiedad, self.valor)
        elif self.tipo == Tipo.SELECTOR:
            self.__preguntar_selector()
            setattr(query, self.propiedad, self.valor.id)
        elif self.tipo == Tipo.SELECTOR_MULTIPLE_PIPE:
            self.__preguntar_selector_multiple()
            lista = "|".join(map(lambda opt: opt.id, self.valor))
            setattr(query, self.propiedad, lista if lista != "" else None)
        elif self.tipo == Tipo.SELECTOR_MULTIPLE_LISTA:
            self.__preguntar_selector_multiple()
            lista = list(map(lambda opt: opt.id, self.valor))
            setattr(query, self.propiedad, lista if len(lista) > 0 else None)

    def __preguntar_selector_multiple(self):
        opts = list(enumerate(self.opciones))
        seleccionadas: Union[str, int, Opcion, List[Opcion]] = self.valor
        while True:
            limpiar()
            print("Opciones disponibles para la condición " + self.nombre + ":")
            for num, opcion in opts:
                seleccionada = len(list(filter(lambda x: x.id == opcion.id, seleccionadas))) > 0
                print("%d - [%s] %s" % (num, "X" if seleccionada else " ", opcion.display))
            valor = input("Introduzca el número correspondiente a la opción que desea seleccionar, o deje en blanco "
                          + "para terminar: ")
            if valor == "":
                break
            try:
                opcion = opts[int(valor)][1]
                encontrada = False
                for seleccionada in seleccionadas[:]:
                    if seleccionada.id == opcion.id:
                        seleccionadas.remove(seleccionada)
                        encontrada = True
                if not encontrada:
                    seleccionadas.append(opcion)
            except IndexError:
                print("La opción seleccionada no existe")
                input("Pulse Intro para continuar...")
            except ValueError:
                print("El valor introducido no es válido. Debe introducir un número entero.")
                input("Pulse Intro para continuar...")
        self.valor = seleccionadas

    def __preguntar_selector(self):
        opts = list(enumerate(self.opciones))
        print("Opciones disponibles para la condición " + self.nombre + ":")
        for num, opcion in opts:
            print("%d - %s" % (num, opcion.display))
        valor = input("Introduzca el número correspondiente a la opción que desea seleccionar: ")
        try:
            self.valor = opts[int(valor)][1]
        except IndexError:
            print("La opción seleccionada no existe")
            input("Pulse Intro para continuar...")
        except ValueError:
            print("El valor introducido no es válido. Debe introducir un número entero.")
            input("Pulse Intro para continuar...")

    def __preguntar_entero(self):
        valor = input("Introduzca el valor para la condición " + self.nombre +
                      ". Deje vacío para no filtrar por esta condición: ")
        if valor == "":
            self.valor = None
        else:
            try:
                self.valor = int(valor)
            except ValueError:
                print("El valor introducido no es válido. Debe introducir un número entero.")
                input("Pulse Intro para continuar...")

    def __preguntar_cadena(self):
        valor = input("Introduzca el valor para la condición " + self.nombre +
                      ". Deje vacío para no filtrar por esta condición: ")
        if valor == "":
            self.valor = None
        else:
            self.valor = valor


class ConstructorQuerys(object):

    def __init__(self, cliente: Site, task_name: str):
        self.query = QueryArticulos(cliente)
        self.cliente = cliente
        self.namespaces = SiteInfo.namespace_list(cliente)
        self.task_name = task_name
        self.condiciones = [
            Condicion("0", "Espacios de nombres", "namespaces", Tipo.SELECTOR_MULTIPLE_LISTA, [],
                      generar_opciones_ns(self.namespaces)),
            Condicion("1", "Desde el artículo", "start"),
            Condicion("2", "Hasta el artículo", "end"),
            Condicion("3", "Cuyo título empiece por", "prefix"),
            Condicion("4", "Filtrado de redirecciones", "filterredir",
                      Tipo.SELECTOR, Opcion("Todas las páginas", "all"),
                      [Opcion("Todas las páginas", "all"), Opcion("No incluir redirecciones", "nonredirects"),
                       Opcion("Solo redirecciones", "redirects")]),
            Condicion("5", "Tamaño mínimo en bytes", "minsize", Tipo.ENTERO),
            Condicion("6", "Tamaño máximo en bytes", "maxsize", Tipo.ENTERO),
            Condicion("7", "Máximo de páginas a devolver", "limit", Tipo.ENTERO),
            Condicion("8", "Dirección en la que ordenar", "dir", Tipo.SELECTOR, Opcion("Ascendiente", "ascending"),
                      [Opcion("Ascendiente", "ascending"), Opcion("Descendiente", "descending")]),
            Condicion("9", "Filtrado de enlaces interwiki", "filterlanglinks", Tipo.SELECTOR,
                      Opcion("Todas las páginas", "all"), [Opcion("Todas las páginas", "all"),
                                                           Opcion("Solo páginas con interwiki", "withlanglinks"),
                                                           Opcion("solo páginas sin interwiki", "withoutlanglinks")]),
            Condicion("A", "Solo páginas protegidas", "prmode", Tipo.BOOLEAN, False),
            Condicion("B", "Acciones protegidas", "prtype", Tipo.SELECTOR_MULTIPLE_PIPE, [Opcion("Edición", "edit")],
                      [Opcion("Edición", "edit"), Opcion("Traslado", "move"), Opcion("Subida", "upload")], "prmode"),
            Condicion("C", "Nivel de protección", "prlevel", Tipo.SELECTOR_MULTIPLE_PIPE, [],
                      [Opcion("Usuarios autoconfirmados", "autoconfirmed"),
                       Opcion("Administradores y moderadores", "sysop")], "prmode")
        ]

    def preguntar_opcion(self) -> Optional[Condicion]:
        limpiar()
        print("%s - Editor de condiciones" % (self.task_name))
        for condicion in self.condiciones:
            condicion.pintar(self.query)
        opcion = input("Introduzca la tecla correspondiente a la opción que desea editar, o ninguna para confirmar: ")
        if opcion == "":
            return None
        else:
            for condicion in self.condiciones:
                if condicion.tecla == opcion and (condicion.depende_de is None
                                                  or getattr(self.query, condicion.depende_de)):
                    return condicion
            raise ValueError()

    def invocar(self) -> QueryArticulos:
        while True:
            try:
                opcion = self.preguntar_opcion()
                if opcion is None:
                    correct = input("Confirma que la consulta es correcta? (s/n): ")
                    if correct == 's':
                        return self.query
                    else:
                        continue
                opcion.preguntar(self.query)
            except ValueError:
                print("La opción introducida no es válida!")
                input("Pulse Intro para continuar...")
