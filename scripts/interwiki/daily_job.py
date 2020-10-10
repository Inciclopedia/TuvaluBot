from common.botmain import BotMain
from common.interwiki.interwikijob import InterwikiJob

NAME = "Interwiki Daily Job"
DESCRIPTION = "This script remaps automatically the interwikis of the articles created in the last day"


class InterwikiDailyJob(InterwikiJob):

    def __init__(self):
        super().__init__()

    def task(self):
        from datetime import datetime, timedelta
        end = datetime.now()
        # three hours margin so we don't miss interwikis between cron jobs
        start = end - timedelta(days=1, hours=3)
        results = self.client.recentchanges(dir="older", namespace='0', type='new', limit=500)
        for article in results:
            if article["timestamp"] > start.timetuple():
                if article["ns"] == 0:
                    self.remap_interwikis(article["title"])


# Don't delete this line or your script won't start
BotMain(DESCRIPTION).start(InterwikiDailyJob())
