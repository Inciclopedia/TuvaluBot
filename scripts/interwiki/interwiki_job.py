from common.principal import Principal
from scripts.interwiki.base_interwiki import BaseInterwiki

DESCRIPTION = "Este bot detecta automáticamente los artículos nuevos del último día en CambiosRecientes y crea los interwikis"


class InterwikiJob(BaseInterwiki):

    def __init__(self):
        super().__init__()

    def tarea(self):
        from datetime import datetime, timedelta
        end = datetime.now()
        # añadimos tres horas de margen para que no se nos escape alguno entre ejecuciones por zona horaria
        start = end - timedelta(days=1, hours=3)
        results = self.cliente.recentchanges(dir="older", namespace='0', type='new', limit=500)
        for article in results:
            if article["timestamp"] > start.timetuple():
                if article["ns"] == 0:
                    self.remapear_pagina(article["title"])


# No borres esta línea o tu script no iniciará:
Principal(DESCRIPTION).iniciar(InterwikiJob())
