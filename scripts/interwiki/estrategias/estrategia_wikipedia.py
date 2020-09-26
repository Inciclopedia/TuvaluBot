from typing import Union, Optional

from mwclient import Site
from mwclient.page import Page

from scripts.interwiki.estrategias.estrategia import Estrategia
from scripts.interwiki.tareainterwiki import TareaInterwiki


class EstrategiaWikipedia(Estrategia):

    def __init__(self, cliente: Site):
        super().__init__(cliente)
        self.clienteWikipedia = Site("es.wikipedia.org")

    def buscar_articulo_en_wikipedia(self, nombre) -> Optional[Page]:
        articulo_wp = Page(self.clienteWikipedia, nombre)
        if articulo_wp.redirect:
            articulo_wp = articulo_wp.resolve_redirect()
        return articulo_wp if articulo_wp.exists else None

    def get_name(self) -> str:
        return "Wikipedia"

    def ejecutar(self, tarea: TareaInterwiki, idioma: str) -> Optional[str]:
        articulo_wp = self.buscar_articulo_en_wikipedia(tarea.pagina.name)
        if articulo_wp is not None:
            interwikis_wp = articulo_wp.langlinks()
            for idioma_wp, destino in interwikis_wp:
                if idioma == idioma_wp:
                    return tarea.buscar_articulo_en_interwiki(idioma, destino)
        return None
