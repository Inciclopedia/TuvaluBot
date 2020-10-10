from common.jobwithquery import JobWithQuery

0

from mwclient.page import Page

from common.botmain import BotMain

NAME = "Cleanup Double Redirects"
DESCRIPTION = "This script removes double redirects"


class CleanupDoubleRedirects(JobWithQuery):

    def __init__(self):
        super().__init__()

    def process(self, article):
        page = Page(self.client, article)
        if not page.redirect:
            return
        self.logger.info(self.lang.t("scripts.cleanupdoubleredirects.processing").format(name=article))
        redirection_chain = []
        while page.redirect:
            if page.name in redirection_chain:
                self.logger.warning(self.lang.t("cleanupdoubleredirects.circular_reference".format(name=article)))
                return
            redirection_chain.append(page.name)
            page = Page(self.client, page.redirects_to())
        if len(redirection_chain) > 1:
            for redirect in redirection_chain[:-1]:
                self.logger.info(self.lang.t("resolving").format(redirect=redirect, target=page.name))
                redir = Page(self.client, redirect)
                redir.edit("#REDIRECT [[" + page.name + "]]", self.lang.t("scripts.cleanupdoubleredirects.reason")
                           .format(target=page.name))

    @property
    def querybuilder_title(self):
        return self.lang.t("scripts.cleanupdoubleredirects.name")


BotMain(DESCRIPTION).start(CleanupDoubleRedirects())
