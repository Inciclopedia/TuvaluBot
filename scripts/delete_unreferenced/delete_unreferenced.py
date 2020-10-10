from common.botmain import BotMain
from common.jobwithquery import JobWithQuery

NAME = "Delete unreferenced pages"
DESCRIPTION = "Deletes pages that are not referenced in other places. PLEASE USE ONLY IN FILE NAMESPACES!"


class DeleteUnreferencedPages(JobWithQuery):

    def __init__(self):
        super().__init__()

    def before_process(self):
        self.logger.warning(self.lang.t("scripts.unreferenced.warning"))
        cont = input(self.lang.t("scripts.unreferenced.confirm"))
        if cont != self.lang.t("scripts.unreferenced.confirmkey"):
            import sys
            sys.exit(1)

    def process(self, article):
        result = self.client.api("query", list="backlinks", bltitle=article)
        if len(result["query"]["backlinks"]) == 0:
            token = self.client.api("query", meta="tokens", type="csrf")["query"]["tokens"]["csrftoken"]
            self.client.api("delete", title=article, reason=self.lang.t("scripts.unreferenced.reason"), token=token)

    @property
    def querybuilder_title(self):
        return self.lang.t("scripts.unreferenced.name")


# Don't delete this line or your script won't start
BotMain(DESCRIPTION).start(DeleteUnreferencedPages())
