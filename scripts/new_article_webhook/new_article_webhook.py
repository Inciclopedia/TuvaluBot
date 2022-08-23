import json
import time
import urllib
from datetime import datetime

import requests

from common.botmain import BotMain
from common.job import Job

DESCRIPTION = "New article Webhook bot"
WEBHOOK = "CONFIGURE_ME"
DRY_RUN = False
NAMESPACES_TO_WATCH = (0, 4, 10, 110, 112, 114, 116)


# Change the class name to your job name, change it also in last line
class NewArticleWebhook(Job):

    def task(self):
        known_new_pages = set()
        to_announce = list()
        try:
            with open("known_new_pages.json", "r") as f:
                known_new_pages = set(json.load(f))
        except:
            known_new_pages = set()
        for page in filter(lambda page: page["ns"] in NAMESPACES_TO_WATCH and page["pageid"] not in known_new_pages,
                           self.client.recentchanges(type="new", limit=100)):
            print(page["title"])
            known_new_pages.add(page["pageid"])
            to_announce.append(page["revid"])
        for revision in self.client.revisions(to_announce):
            payload = {
                "content": None,
                "embeds": [
                    {
                        "title": revision["pagetitle"][:256],
                        "description": revision["comment"][:4096],
                        "color": 0,
                        "url": "https://inciclopedia.org/wiki/" + urllib.parse.quote(revision["pagetitle"]),
                        "author": {
                            "name": revision["user"],
                            "url": "https://inciclopedia.org/wiki/Usuario:" + urllib.parse.quote(revision["user"])
                        },
                        "footer": {
                            "text": "Página nueva"
                        },
                        "timestamp": datetime.fromtimestamp(time.mktime(revision["timestamp"])).isoformat()
                    }
                ],
            }
            if not DRY_RUN:
                result = requests.post(WEBHOOK, data=json.dumps(payload),
                                       headers={"Content-Type": "application/json;charset=UTF-8"})
                pass
            else:
                print("DRY RUN - NO SE HIZO NINGUNA PETICIÓN AL WEBHOOK")
            time.sleep(2)

        with open("known_new_pages.json", "w") as f:
            json.dump(list(known_new_pages), f)


# Don't delete this line or your script won't start
BotMain(DESCRIPTION).start(NewArticleWebhook())
