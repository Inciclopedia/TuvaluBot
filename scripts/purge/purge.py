from mwclient.page import Page

from common.botmain import BotMain
from common.jobwithquery import JobWithQuery

NAME = "Purge"
DESCRIPTION = "This script purges the given articles"


class Purge(JobWithQuery):

    @property
    def querybuilder_title(self):
        return self.lang.t("scripts.purge.name")

    def __init__(self):
        super().__init__()

    def process(self, article):
        page = Page(self.client, article)
        page.purge()
        self.logger.info(self.lang.t("common.processed").format(name=article))


BotMain(DESCRIPTION).start(Purge())
