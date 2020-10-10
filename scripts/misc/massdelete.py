from common.botmain import BotMain
from common.jobwithquery import JobWithQuery

NAME = "Delete page"
DESCRIPTION = "This script deletes all the pages from the given query with the given protection level"
REASON = "Juzgado en VPB"


class MassDelete(JobWithQuery):

    def __init__(self):
        super().__init__()

    def before_process(self):
        self.logger.warning(self.lang.t("scripts.massdelete.warning"))
        cont = input(self.lang.t("scripts.massdelete.confirm"))
        if cont != self.lang.t("scripts.massdelete.confirmkey"):
            import sys
            sys.exit(1)

    def process(self, page_name):
        token = self.client.api("query", meta="tokens", type="csrf")["query"]["tokens"]["csrftoken"]
        self.client.api("delete", title=page_name, reason=REASON, token=token)
        self.logger.info(self.lang.t("common.processed").format(name=page_name))

    @property
    def querybuilder_title(self):
        return self.lang.t("scripts.massdelete.name")


BotMain(DESCRIPTION).start(MassDelete())
