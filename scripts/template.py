from common.botmain import BotMain
from common.job import Job

DESCRIPTION = "Describe your task here"


# Change the class name to your job name, change it also in last line
class Template(Job):

    def task(self):
        # Your code goes here
        pass


# Don't delete this line or your script won't start
BotMain(DESCRIPTION).start(Template())
