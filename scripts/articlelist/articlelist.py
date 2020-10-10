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

    @property
    @inject.param('lang', Lang)
    def querybuilder_title(self, lang: Lang = None):
        return lang.t("scripts.articlelist.name")

    def process(self, article):
        self.file.write(article + "\n")

    @inject.param('lang', Lang)
    def after_process(self, lang: Lang = None):
        print(lang.t("scripts.articlelist.task_completed").format(fname=self.fname))
        self.file.close()


# Don't delete this line or your script won't start
BotMain(DESCRIPTION).start(ArticleList())
