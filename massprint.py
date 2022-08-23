import json
from urllib.parse import quote

from selenium import webdriver

CHROMEDRIVER_PATH = 'c:\\chromedriver\\chromedriver.exe'
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
         'savefile.default_directory': 'c:\\destacados'}
chrome_options.add_experimental_option('prefs', prefs)
chrome_options.add_argument('--kiosk-printing')
driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=CHROMEDRIVER_PATH)
with open("destacados.txt", "r", encoding="utf-8") as f:
    for line in f.readlines():
        print(line)
        driver.get("https://inciclopedia.org/wiki/" + quote(line.strip()))
        driver.execute_script('window.print();')
driver.close()
