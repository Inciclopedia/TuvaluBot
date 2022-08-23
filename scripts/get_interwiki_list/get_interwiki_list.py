import csv

import inject
from mwclient.page import Page

from common.botmain import BotMain
from common.jobwithquery import JobWithQuery
from util.lang import Lang

NAME = "Get Interwikis"
DESCRIPTION = "This job gets the list of interwikis of each article and stores it in a CSV format"


class TemplateWithQuery(JobWithQuery):

    def __init__(self):
        super().__init__()

    @inject.param('lang', Lang)
    def before_process(self, lang: Lang = None):
        self.fname = input(lang.t("scripts.articlelist.choose_path"))
        self.file = open(self.fname, "w", encoding="utf-8", newline='')
        fieldnames = ["article", "total_interwiki_links", "interwikis"]
        csv.register_dialect('semicolon', delimiter=';', quoting=csv.QUOTE_MINIMAL)
        self.writer = csv.DictWriter(self.file, fieldnames=fieldnames, dialect="semicolon")
        self.writer.writeheader()

    def process(self, article):
        print(article)
        page = Page(self.client, article)
        links = list(page.langlinks())
        iwlinks = list(map(lambda x: x[0], links))
        record = dict()
        record["article"] = article
        record["total_interwiki_links"] = len(iwlinks)
        record["interwikis"] = "-".join(iwlinks)
        self.writer.writerow(record)

    @property
    def querybuilder_title(self):
        # Ideally you would add in your JSON the translations and use this:
        # return self.lang.t("scripts.yourscriptname.name")
        # If you feel lazy, hardcode the value
        return "Script"


# Don't delete this line or your script won't start
BotMain(DESCRIPTION).start(TemplateWithQuery())
