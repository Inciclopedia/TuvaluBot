from common.botmain import BotMain
from common.jobwithquery import JobWithQuery

NAME = "Type a name for your script"
DESCRIPTION = "Type a description for your script"


class TemplateWithQuery(JobWithQuery):

    def __init__(self):
        super().__init__()

    def process(self, article):
        # your code for each article goes here
        pass

    @property
    def querybuilder_title(self):
        # Ideally you would add in your JSON the translations and use this:
        # return self.lang.t("scripts.yourscriptname.name")
        # If you feel lazy, hardcode the value
        return "Script"


# Don't delete this line or your script won't start
BotMain(DESCRIPTION).start(TemplateWithQuery())
