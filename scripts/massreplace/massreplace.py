from typing import re

from common.botmain import BotMain
from common.jobwithquery import JobWithQuery

NAME = "Reemplazo masivo"
DESCRIPTION = "Reemplazo masivo"


class TemplateWithQuery(JobWithQuery):

    def __init__(self):
        super().__init__()
        self.regex = False
        self.search = ""
        self.replace = ""
        self.reason = ""

    def before_process(self):
        self.regex = input("¿Desea buscar utilizando expresiones regulares? Si no sabe lo que significa, elija n (s/n)").lower() == "s"
        self.search = input("Introduzca la cadena a buscar: ")
        self.replace = input("Introduzca la cadena de reemplazo: ")
        self.reason = input("Introduzca el motivo de edición: ")

    def process(self, article):
        # your code for each article goes here
        page = self.client.pages[article]
        text = page.text()
        if self.regex:
            text = re.sub(self.search, self.replace, text)
        else:
            text = text.replace(self.search, self.replace)
        page.edit(text, self.reason)

    @property
    def querybuilder_title(self):
        # Ideally you would add in your JSON the translations and use this:
        # return self.lang.t("scripts.yourscriptname.name")
        # If you feel lazy, hardcode the value
        return self.lang.t("scripts.massreplace.name")


# Don't delete this line or your script won't start
BotMain(DESCRIPTION).start(TemplateWithQuery())
