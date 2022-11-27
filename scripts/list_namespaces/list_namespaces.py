from common.botmain import BotMain
from common.job import Job
from util.siteinfo import SiteInfo

DESCRIPTION = "Describe your task here"


# Change the class name to your job name, change it also in last line
class Template(Job):

    def task(self):
        for ns in SiteInfo.namespace_list(self.client):
            print(str(ns.id) + " - " + str(ns.canonical_name if ns.canonical_name else "unnamed"))


# Don't delete this line or your script won't start
BotMain(DESCRIPTION).start(Template())
