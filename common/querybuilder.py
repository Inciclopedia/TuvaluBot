import os
from enum import Enum
from typing import List, Union, Optional, Iterable

import inject
from mwclient import Site

from domain.articlequery import ArticleQuery
from domain.namespace import Namespace
from util.lang import Lang
from util.siteinfo import SiteInfo


def clrscr():
    os.system('cls' if os.name == 'nt' else 'clear')


class Type(Enum):
    STRING = 1
    INTEGER = 2
    SELECTOR = 3
    MULTIPLE_PIPE_SELECTOR = 4
    BOOLEAN = 5
    MULTIPLE_LIST_SELECTOR = 6


class Option(object):

    def __init__(self, display, id):
        self.display = display
        self.id = id


def generar_opciones_ns(namespaces: Iterable[Namespace]):
    lista = []
    for namespace in namespaces:
        lista.append(Option(namespace.site_name, namespace.id))
    return lista


class Condition(object):

    @inject.param("lang", Lang)
    def __init__(self, key, name, prop, dtype=Type.STRING, value=None, options: List[Option]=None,
                 depends_on=None, lang: Lang = None):
        self.key = key
        self.name = name
        self.dtype = dtype
        self.value: Union[str, int, Option, bool, List[Option]] = value
        self.property = prop
        self.options = options
        self.depends_on = depends_on
        self.lang = lang

    def pintar(self, query: ArticleQuery):
        if self.depends_on is not None and getattr(query, self.depends_on) is False:
            return
        if self.dtype == Type.STRING:
            print("%s - %s: [%.40s]" % (self.key, self.name, self.value or "",))
        elif self.dtype == Type.INTEGER:
            print("%s - %s: [%.40s]" % (self.key, self.name, str(self.value) if self.value is not None else "",))
        elif self.dtype == Type.SELECTOR:
            print("%s - %s: [%.40s]" % (self.key, self.name, self.value.display))
        elif self.dtype == Type.MULTIPLE_PIPE_SELECTOR or self.dtype == Type.MULTIPLE_LIST_SELECTOR:
            disp = []
            for opcion in self.value:
                for opt in self.options:
                    if opcion.id == opt.id:
                        disp.append(opcion.display)
            print("%s - %s: [%.40s]" % (self.key, self.name, ", ".join(disp),))
        elif self.dtype == Type.BOOLEAN:
            print("%s - [%s] %s" % (self.key, "X" if self.value else " ", self.name))

    def ask(self, query: ArticleQuery):
        clrscr()
        if self.dtype == Type.STRING:
            self.__ask_string()
            setattr(query, self.property, self.value)
        elif self.dtype == Type.INTEGER:
            self.__ask_int()
            setattr(query, self.property, self.value)
        elif self.dtype == Type.BOOLEAN:
            self.value = not self.value
            setattr(query, self.property, self.value)
        elif self.dtype == Type.SELECTOR:
            self.__ask_single_choice()
            setattr(query, self.property, self.value.id)
        elif self.dtype == Type.MULTIPLE_PIPE_SELECTOR:
            self.__ask_multiple_choice()
            lst = "|".join(map(lambda opt: opt.id, self.value))
            setattr(query, self.property, lst if lst != "" else None)
        elif self.dtype == Type.MULTIPLE_LIST_SELECTOR:
            self.__ask_multiple_choice()
            lst = list(map(lambda opt: opt.id, self.value))
            setattr(query, self.property, lst if len(lst) > 0 else None)

    def __ask_multiple_choice(self):
        opts = list(enumerate(self.options))
        seleccionadas: Union[str, int, Option, List[Option]] = self.value
        while True:
            clrscr()
            print(self.lang.t("querybuilder.options_available").format(name=self.name))
            for num, opcion in opts:
                seleccionada = len(list(filter(lambda x: x.id == opcion.id, seleccionadas))) > 0
                print("%d - [%s] %s" % (num, "X" if seleccionada else " ", opcion.display))
            valor = input(self.lang.t("querybuilder.input_choice"))
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
                print(self.lang.t("common.option_does_not_exist"))
                input(self.lang.t("common.press_enter"))
            except ValueError:
                print(self.lang.t("common.type_a_number"))
                input(self.lang.t("common.press_enter"))
        self.value = seleccionadas

    def __ask_single_choice(self):
        opts = list(enumerate(self.options))
        print(self.lang.t("querybuilder.options_available").format(name=self.name))
        for num, opcion in opts:
            print("%d - %s" % (num, opcion.display))
        valor = input(self.lang.t("querybuilder.input_choice"))
        try:
            self.value = opts[int(valor)][1]
        except IndexError:
            print(self.lang.t("common.option_does_not_exist"))
            input(self.lang.t("common.press_enter"))
        except ValueError:
            print(self.lang.t("common.type_a_number"))
            input(self.lang.t("common.press_enter"))

    def __ask_int(self):
        valor = input(self.lang.t("querybuilder.input_value").format(name=self.name))
        if valor == "":
            self.value = None
        else:
            try:
                self.value = int(valor)
            except ValueError:
                print(self.lang.t("common.type_a_number"))
                input(self.lang.t("common.press_enter"))

    def __ask_string(self):
        valor = input(self.lang.t("querybuilder.input_value").format(name=self.name))
        if valor == "":
            self.value = None
        else:
            self.value = valor


class QueryBuilder(object):

    @inject.param('lang', Lang)
    def __init__(self, client: Site, task_name: str, lang: Lang = None):
        self.lang = lang
        self.query = ArticleQuery(client)
        self.cliente = client
        self.namespaces = SiteInfo.namespace_list(client)
        self.task_name = task_name
        # this is a lambda for abbreviation aka i'm lazy to type all the thing
        q = lambda key: lang.t("querybuilder.queries.{key}".format(key=key))
        self.condiciones = [
            Condition("0", q("namespaces"), "namespaces", Type.MULTIPLE_LIST_SELECTOR, [],
                      generar_opciones_ns(self.namespaces)),
            Condition("1", q("start"), "start"),
            Condition("2", q("end"), "end"),
            Condition("3", q("prefix"), "prefix"),
            Condition("4", q("filterredir"), "filterredir",
                      Type.SELECTOR, Option(q("all"), "all"),
                      [Option(q("all"), "all"), Option(q("nonredirects"), "nonredirects"),
                       Option(q("redirects"), "redirects")]),
            Condition("5", q("minsize"), "minsize", Type.INTEGER),
            Condition("6", q("maxsize"), "maxsize", Type.INTEGER),
            Condition("7", q("limit"), "limit", Type.INTEGER),
            Condition("8", q("dir"), "dir", Type.SELECTOR, Option(q("ascending"), "ascending"),
                      [Option("Ascendiente", "ascending"), Option(q("descending"), "descending")]),
            Condition("9", q("filterlanglinks"), "filterlanglinks", Type.SELECTOR,
                      Option(q("all"), "all"), [Option(q("all"), "all"),
                                                Option(q("withlanglinks"), "withlanglinks"),
                                                Option(q("withoutlanglinks"), "withoutlanglinks")]),
            Condition("A", q("prmode"), "prmode", Type.BOOLEAN, False),
            Condition("B", q("prtype"), "prtype", Type.MULTIPLE_PIPE_SELECTOR, [Option(q("edit"), "edit")],
                      [Option(q("edit"), "edit"), Option(q("move"), "move"), Option(q("upload"), "upload")], "prmode"),
            Condition("C", q("prlevel"), "prlevel", Type.MULTIPLE_PIPE_SELECTOR, [],
                      [Option(q("autoconfirmed"), "autoconfirmed"),
                       Option(q("sysop"), "sysop")], "prmode"),
            Condition("D", q("category"), "category")
        ]

    def __ask_option(self) -> Optional[Condition]:
        clrscr()
        print(self.lang.t("querybuilder.title").format(taskname=self.task_name))
        for condicion in self.condiciones:
            condicion.pintar(self.query)
        opcion = input(self.lang.t("querybuilder.choose_option"))
        if opcion == "":
            return None
        else:
            for condicion in self.condiciones:
                if condicion.key == opcion and (condicion.depends_on is None
                                                or getattr(self.query, condicion.depends_on)):
                    return condicion
            raise ValueError()

    def invoke(self) -> ArticleQuery:
        while True:
            try:
                option = self.__ask_option()
                if option is None:
                    correct = input(self.lang.t("querybuilder.confirm_query"))
                    if correct == self.lang.t("querybuilder.confirm_query_key"):
                        return self.query
                    else:
                        continue
                option.ask(self.query)
            except ValueError:
                print(self.lang.t("common.option_does_not_exist"))
                input(self.lang.t("common.press_enter"))
