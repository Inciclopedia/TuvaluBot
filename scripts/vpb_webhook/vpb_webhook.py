import json
import re
import textwrap
import time
import urllib
from datetime import datetime

import requests
from dewiki import from_string

from common.botmain import BotMain
from common.job import Job

DESCRIPTION = "VPB Webhook bot"
WEBHOOK = "CONFIGURE_ME"
DRY_RUN = False


# Change the class name to your job name, change it also in last line
class VPBWebhook(Job):

    def task(self):
        # Your code goes here
        try:
            with open("votes.json", "r", encoding="utf8") as f:
                current_nominees = json.load(f)
        except:
            current_nominees = {
                "VPB": [],
                "VPD": [],
                "VPA": [],
                "Escritor del mes": [],
                "Inciclopedista del mes": [],
                "Novato del mes": []
            }
        current_nominees = self.process_votes("Inciclopedia:VPB", "VPB", "Juicios", "Nominaciones para borrado rápido",
                                              "articulo", "", current_nominees, "7a0800")
        current_nominees = self.process_votes("Inciclopedia:VPD", "VPD", "Nominados", "Destacados recientes",
                                              "articulo", "", current_nominees, "004f12")
        current_nominees = self.process_votes("Inciclopedia:VPA", "VPA", "Juzgándose", "Aprobados", "usuario",
                                              "Usuario:", current_nominees, "000261")
        current_nominees = self.process_votes("Inciclopedia:Escritor_e_Inciclopedista_del_mes", "Escritor del mes",
                                              "Escritor del mes", "Inciclopedista del mes", "usuario", "Usuario:",
                                              current_nominees, "00694b")
        current_nominees = self.process_votes("Inciclopedia:Escritor_e_Inciclopedista_del_mes",
                                              "Inciclopedista del mes", "Inciclopedista del mes", "Novato del mes",
                                              "usuario", "Usuario:", current_nominees, "c79500")
        current_nominees = self.process_votes("Inciclopedia:Escritor_e_Inciclopedista_del_mes", "Novato del mes",
                                              "Novato del mes", "Cuadro de honor", "usuario", "Usuario:",
                                              current_nominees, "be5cff")
        with open("votes.json", "w", encoding="utf8") as f:
            json.dump(current_nominees, f)

    def process_votes(self, page_name, friendly_name, starts_at, stops_at, nominee_type, prefix, current_nominees,
                      embed_color):
        print("Procesando " + page_name)
        wikitext = self.client.pages.get(page_name).text()
        level = None
        nominations = []
        for raw_line in wikitext.splitlines():
            line = raw_line.strip()
            if level is None:
                start = re.findall(r'=+\s*' + starts_at + r'\s*=+', line, flags=re.IGNORECASE)
                if len(start) > 0:
                    level = len(start[0])
                continue
            nomination = re.findall(r'=+\s*\[\[([^\]]+)\]\]\s*=+', line, flags=re.IGNORECASE)
            nomination += re.findall(r'=+\s*\{\{u\|([^\}]+)\}\}\s*=+', line, flags=re.IGNORECASE)
            if len(nomination) > 0:
                print("Nominación: " + nomination[0])
                nominations.append(nomination[0])
                if nomination[0] not in current_nominees[friendly_name]:
                    print("No está en conocidos, anunciando:")
                    encoded = urllib.parse.quote(nomination[0])
                    try:
                        maybe_article = self.client.pages.get(f"{prefix}{nomination[0]}")
                    except:
                        maybe_article = ""
                    payload = {
                        "content": None,
                        "embeds": [{
                            "title": nomination[0],
                            "description": textwrap.shorten(from_string(maybe_article.text()), width=500),
                            "url": f"https://inciclopedia.org/wiki/{prefix}{encoded}",
                            "color": int(embed_color, 16),
                            "author": {
                                "name": f"Se ha nominado un {nominee_type} en {friendly_name}",
                                "url": "https://inciclopedia.org/wiki/" + page_name,
                                "icon_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b8/Dark_blue_right_arrow.svg/120px-Dark_blue_right_arrow.svg.png"
                            },
                            "footer": {
                                "text": page_name,
                                "icon_url": "https://images.uncyclomedia.co/inciclopedia/es/b/bc/Wiki.png"
                            },
                            "timestamp": datetime.now().isoformat()
                        }]
                    }
                    print("Enviando POST al webhook con payload:")
                    print(json.dumps(payload))
                    if not DRY_RUN:
                        result = requests.post(WEBHOOK, data=json.dumps(payload),
                                               headers={"Content-Type": "application/json;charset=UTF-8"})
                    else:
                        print("DRY RUN - NO SE HIZO NINGUNA PETICIÓN AL WEBHOOK")
                    time.sleep(2)
                    print("Enviado POST al webhook con respuesta " + str(result.status_code))
                    print("Cuerpo de la respuesta:")
                    print(result.text)
                continue
            closure = re.findall(r'=+\s*' + stops_at + r'\s*=+', line, flags=re.IGNORECASE)
            if len(closure) > 0:
                break
        current_nominees[friendly_name] = nominations
        return current_nominees


# Don't delete this line or your script won't start
BotMain(DESCRIPTION).start(VPBWebhook())
