import re

from mwclient.page import Page

from common.botmain import BotMain
from common.jobwithquery import JobWithQuery

NAME = "List Pictures"
DESCRIPTION = "List the pictures of the given articles (good to use with delete unreferenced)"


class ListPictures(JobWithQuery):

    def __init__(self):
        super().__init__()
        self.file = None
        self.fname = None

    def process(self, article):
        page = Page(self.client, article)
        wikitext = page.text()
        matches = re.search(r"\[\[((?:[^\]|$]+)(?=.png|.jpg|.jpeg|.gif|.svg).png|.jpg|.jpeg|.gif|svg)(?:|[^\]$]+)\]\]", wikitext)
        if matches:
            for match in matches.groups():
                self.file.write(match + "\n")

    def before_process(self):
        self.fname = input(self.lang.t("scripts.articlelist.choose_path"))
        self.file = open(self.fname, "w", encoding="utf-8")

    def after_process(self):
        print(self.lang.t("scripts.articlelist.task_completed").format(fname=self.fname))
        self.file.close()

    @property
    def querybuilder_title(self):
        # Ideally you would add in your JSON the translations and use this:
        # return self.lang.t("scripts.yourscriptname.name")
        # If you feel lazy, hardcode the value
        return "List Pictures"


# Don't delete this line or your script won't start
BotMain(DESCRIPTION).start(ListPictures())
