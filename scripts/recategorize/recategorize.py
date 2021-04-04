import os
import sys
import webbrowser
from os import system
from tempfile import NamedTemporaryFile
from typing import IO
from urllib.parse import quote
import re

import inject
from mwclient.page import Page

from common.botmain import BotMain
from common.jobwithquery import JobWithQuery
from common.querybuilder import clrscr
from util.configimpl import Config

DESCRIPTION = "Recategorizador interactivo de artículos"


class Recategorize(JobWithQuery):

    def __init__(self):
        super().__init__()
        self.interactive = False
        self.massive_file = None
        self.query = None
        self.category_name = 'Category:'

    @inject.param('config', Config)
    def before_process(self, config: Config = None):
        self.category_name = config.config["wiki"]["category_name"]
        clrscr()
        print(self.lang.t("scripts.recategorize.name"))
        print()
        print(self.lang.t("scripts.recategorize.choosemode"))
        print()
        print(self.lang.t("scripts.recategorize.chooseinteractive"))
        print(self.lang.t("scripts.recategorize.choosemassive"))
        print(self.lang.t("scripts.recategorize.choosequit"))
        option = input(self.lang.t("common.type_query"))
        while option not in ("1", "2", "3"):
            print(self.lang.t("common.option_does_not_exist"))
            option = input("Seleccione su preferencia: ")
        if option == "1":
            self.interactive = True
        elif option == "2":
            self.interactive = False
            self.massive_file: IO = NamedTemporaryFile(mode="w", delete=False, encoding="windows-1252")
        elif option == "3":
            sys.exit(0)

    @inject.param('config', Config)
    def get_url(self, name: str, config: Config = None):
        return "https://{api}/wiki/{name}".format(api=config.config["wiki"]["api"], name=quote(name))

    def process(self, article: str):
        if self.interactive:
            key = ""
            additions, removals = [], []
            page = self.client.pages[article]
            while not key == self.lang.t("querybuilder.confirm_query_key"):
                clrscr()
                self.print_article(page)
                self.ask_query(self.get_url(article))
                if self.query == "":
                    key = input(self.lang.t("querybuilder.do_nothing")).lower()
                else:
                    additions, removals = self.get_recategorization(page, self.query)
                    print("Acciones a realizar:")
                    self.print_recategorization(additions, removals)
                    key = input(self.lang.t("querybuilder.confirm_query")).lower()
            self.do_recategorize(page, additions, removals)
        else:
            self.massive_file.write(article + "\n")

    def print_article(self, article: Page):
        print(self.lang.t("scripts.recategorize.articleinfo.name") + article.name)
        print("-".join(map(lambda _: "", range(80))))
        print(self.preview(article))
        print("-".join(map(lambda _: "", range(80))))
        print(self.lang.t("scripts.recategorize.articleinfo.current_categories") +
              ",".join(list(map(lambda x: "".join(x.name.split(":")[1:]), article.categories()))))

    def preview(self, article: Page):
        text = article.text()
        lines = []
        for line in text.splitlines():
            curline = line
            while len(curline) > 80:
                lines.append(curline[:80])
                curline = curline[80:]
            lines.append(curline)
        return os.linesep.join(lines[:15])

    def after_process(self):
        if not self.interactive:
            clrscr()
            print(self.lang.t("scripts.recategorize.notepad"))
            self.massive_file.close()
            system("notepad " + self.massive_file.name)
            input(self.lang.t("common.press_enter"))
            self.ask_query()
            with open(self.massive_file.name, "r") as f:
                for line in f.readlines():
                    print("Recategorizando " + line.strip() + ":")
                    page = self.client.pages[line.strip()]
                    additions, removals = self.get_recategorization(page, self.query)
                    self.print_recategorization(additions, removals)
                    self.do_recategorize(page, additions, removals)

    def get_recategorization(self, article: Page, query: str):
        actions = query.split(",")
        addition_candidates = list(map(lambda x: self.category_name + x[1:], filter(lambda x: x.strip()[0] == '+', actions)))
        removal_candidates = list(map(lambda x: x[1:].lower().strip(), filter(lambda x: x.strip()[0] == '-', actions)))
        categories = list(map(lambda x: x.name, article.categories()))
        additions = filter(lambda x: x.lower().strip() not in map(lambda y: y.lower().strip(), categories),
                           addition_candidates)
        removals = filter(lambda x: ("".join(x.split(':')[1:])).lower().strip() in removal_candidates, categories)
        return list(additions), list(removals)

    def print_recategorization(self, additions, removals):
        for addition in additions:
            print("   Añadir categoría " + addition)
        for removal in removals:
            print("   Eliminar categoría " + removal)

    def do_recategorize(self, article: Page, additions, removals):
        if self.query == "":
            return
        print("Guardando...")
        wikitext = article.text()
        for removal in removals:
            wikitext = re.sub(r'\[\[' + removal + r'(?:|.*)*\]\]', '', wikitext)
        for addition in additions:
            wikitext = wikitext + "\n[[{}]]".format(addition)
        plainadditions = ",".join(map(lambda x: "+" + ",".join(x.split(':')[1:]), additions))
        plainremovals = ",".join(map(lambda x: "-" + ",".join(x.split(':')[1:]), removals))
        query = plainadditions + "; " + plainremovals
        article.edit(wikitext, summary=self.lang.t("scripts.recategorize.reason") + query, minor=True)

    @property
    def querybuilder_title(self):
        return self.lang.t("scripts.recategorize.name")

    def validate_query(self, query, browser):
        if not query or len(query) == 0:
            return False
        if query.lower() == 'n':
            webbrowser.open(browser)
            return False
        for subquery in query.split(','):
            if subquery.strip()[0] not in ('+', '-'):
                print(self.lang.t("scripts.recategorize.category_validation_error"))
                return False
        return True

    def ask_query(self, browser=None):
        print(self.lang.t("scripts.recategorize.category_query_help"))
        print(self.lang.t("scripts.recategorize.category_query_example"))
        if browser:
            print(self.lang.t("scripts.recategorize.category_query_browser"))
        self.query = None
        while not self.validate_query(self.query, browser):
            self.query = input(self.lang.t("common.type_query"))
            if self.query == "":
                return


BotMain(DESCRIPTION).start(Recategorize())
