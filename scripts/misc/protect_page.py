from common.botmain import BotMain
from common.jobwithquery import JobWithQuery

NAME = "Protect page"
DESCRIPTION = "This script protects all the pages from the given query with the given protection level"
PRLEVEL = "edit=sysop|move=sysop"
REASON = "Bot's fault"


class ProtectPage(JobWithQuery):

    def __init__(self):
        super().__init__()

    def process(self, page_name):
        token = self.client.api("query", meta="tokens", type="csrf")["query"]["tokens"]["csrftoken"]
        self.client.api("protect", title=page_name, protections=PRLEVEL, reason=REASON, token=token)

    @property
    def querybuilder_title(self):
        return self.lang.t("scripts.protectpage.name")


BotMain(DESCRIPTION).start(ProtectPage())
