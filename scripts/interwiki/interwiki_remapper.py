from mwclient import LoginError

from common.botmain import BotMain
from common.interwiki.interwikijob import InterwikiJob
from common.jobwithquery import JobWithQuery

DESCRIPTION = "This script remaps all interwikis from the given query"


class InterwikiRemapper(InterwikiJob, JobWithQuery):

    @property
    def querybuilder_title(self):
        return self.lang.t("interwiki.querybuilder_title")

    def process(self, article):
        try:
            self.client.login(self.client.username, self.password)
        except LoginError:
            pass
        try:
            self.remap_interwikis(article)
        except Exception as e:
            self.logger.error(str(e))

    def __init__(self):
        super().__init__()


BotMain(DESCRIPTION).start(InterwikiRemapper())
