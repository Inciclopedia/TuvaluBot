import time

from common.botmain import BotMain
from common.job import Job

NAME = "Mass block"
DESCRIPTION = "This script blocks all users from a given list"
REASON = "Bloqueado por ser sospechoso de SPAM, si crees que fue un error, envía un ticket a https://inciclopedia.atlassian.net/servicedesk/customer/portal/1/group/6/create/17"


class MassBlock(Job):

    def __init__(self):
        super().__init__()

    def task(self):
        self.logger.warning(self.lang.t("scripts.massblock.warning"))
        cont = input(self.lang.t("scripts.massblock.confirm"))
        if cont != self.lang.t("scripts.massblock.confirmkey"):
            import sys
            sys.exit(1)
        token = self.client.api("query", meta="tokens", type="csrf")["query"]["tokens"]["csrftoken"]
        with open("blocklist.txt", "r", encoding="utf-8") as f:
            for line in f.readlines():
                target = line.strip()
                self.client.api("block", user=target, reason=REASON, token=token, nocreate=True, autoblock=True,
                                allowusertalk=False, reblock=True)
                print("Bloqueado " + target)
                time.sleep(1)


BotMain(DESCRIPTION).start(MassBlock())
