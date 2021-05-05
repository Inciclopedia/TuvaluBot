from urllib.parse import quote

from common.botmain import BotMain
from common.jobwithquery import JobWithQuery
from selenium import webdriver
import json

NAME = "Print article"
DESCRIPTION = "Prints the article"
CHROMEDRIVER_PATH = 'c:\\chromedriver\\chromedriver.exe'


class TemplateWithQuery(JobWithQuery):

    def __init__(self):
        super().__init__()
        chrome_options = webdriver.ChromeOptions()
        settings = {
            "recentDestinations": [{
                "id": "Save as PDF",
                "origin": "local",
                "account": "",
            }],
            "selectedDestinationId": "Save as PDF",
            "version": 2
        }
        prefs = {'printing.print_preview_sticky_settings.appState': json.dumps(settings),
                 'savefile.default_directory': 'c:\\inciclopedia'}
        chrome_options.add_experimental_option('prefs', prefs)
        chrome_options.add_argument('--kiosk-printing')
        self.driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=CHROMEDRIVER_PATH)

    def process(self, article):
        # your code for each article goes here
        self.driver.get("https://inciclopedia.org/wiki/" + quote(article))
        self.driver.execute_script('window.print();')

    @property
    def querybuilder_title(self):
        # Ideally you would add in your JSON the translations and use this:
        # return self.lang.t("scripts.yourscriptname.name")
        # If you feel lazy, hardcode the value
        return "Print article"


# Don't delete this line or your script won't start
BotMain(DESCRIPTION).start(TemplateWithQuery())
