import inject

from common.botmain import BotMain
from common.jobwithquery import JobWithQuery
from util.lang import Lang

NAME = "Article Count"
DESCRIPTION = "Generates a real count of articles from the given query"


class ArticleList(JobWithQuery):

    def __init__(self):
        super().__init__()
        self.file = None
        self.fname = None

    @inject.param('lang', Lang)
    def before_process(self, lang: Lang = None):
        self.ct = 0

    @property
    @inject.param('lang', Lang)
    def querybuilder_title(self, lang: Lang = None):
        return lang.t("scripts.articlelist.name")

    def process(self, article):
        self.ct += 1

    @inject.param('lang', Lang)
    def after_process(self, lang: Lang = None):
        print(lang.t("scripts.articlelist.task_completed").format(fname=self.fname))
        print("Total %d" % self.ct)


# Don't delete this line or your script won't start
BotMain(DESCRIPTION).start(ArticleList())
