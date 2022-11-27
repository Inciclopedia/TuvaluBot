import inject

from common.botmain import BotMain
from common.jobwithquery import JobWithQuery
from util.lang import Lang

NAME = "Article Listing"
DESCRIPTION = "Generates a list of articles from the given query"


class ArticleList(JobWithQuery):

    def __init__(self):
        super().__init__()
        self.file = None
        self.fname = None

    @inject.param('lang', Lang)
    def before_process(self, lang: Lang = None):
        self.fname = input(lang.t("scripts.articlelist.choose_path"))
        self.file = open(self.fname, "w", encoding="utf-8")
        self.dct = dict()
        self.c = 0

    @property
    @inject.param('lang', Lang)
    def querybuilder_title(self, lang: Lang = None):
        return lang.t("scripts.articlelist.name")

    def process(self, article):
        self.c += 1
        if self.c % 50 == 0:
            print("procesados %d" % self.c)
        red = self.client.pages[article]
        redir = red.redirects_to()
        if redir is not None:
            if redir.name not in self.dct:
                self.dct[redir.name] = list()
            self.dct[redir.name].append("%s (%d)" % (article, len(list(red.backlinks()))))

    @inject.param('lang', Lang)
    def after_process(self, lang: Lang = None):
        for article, redirs in sorted(self.dct.items(), key=lambda x: len(x[1]), reverse=True):
            self.file.write("%s (%d): %s\n" % (article, len(redirs), ", ".join(redirs)))
        print(lang.t("scripts.articlelist.task_completed").format(fname=self.fname))
        self.file.close()


# Don't delete this line or your script won't start
BotMain(DESCRIPTION).start(ArticleList())
