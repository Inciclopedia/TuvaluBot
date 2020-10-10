from mwclient.page import Page

from common.botmain import BotMain
from common.jobwithquery import JobWithQuery

NAME = "Add template"
DESCRIPTION = "This script adds the chosen template in all articles"
TEMPLATE = "{{PutYourTemplateNameHere}}"
BEGINNING = True


class AddTemplate(JobWithQuery):

    def __init__(self):
        super().__init__()

    @property
    def querybuilder_title(self):
        return self.lang.t("scripts.addtemplate.name")

    def process(self, page_name):
        page = Page(self.client, page_name)
        wikitext = page.text()
        if BEGINNING:
            wikitext = TEMPLATE + "\n" + wikitext
        else:
            wikitext = wikitext + "\n" + TEMPLATE
        page.edit(wikitext, summary=self.lang.t("scripts.addtemplate.summary").format(template=TEMPLATE))


BotMain(DESCRIPTION).start(AddTemplate())
