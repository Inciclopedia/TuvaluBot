from typing import Union, Optional

from mwclient import Site

from scripts.interwiki.estrategias.estrategia import Estrategia
from scripts.interwiki.tareainterwiki import TareaInterwiki
from googletrans import Translator


class EstrategiaTraduccion(Estrategia):

    def __init__(self, cliente: Site):
        super().__init__(cliente)
        self.translator = Translator()

    def ejecutar(self, tarea: TareaInterwiki, idioma: str) -> Optional[str]:
        try:
            traduccion = self.translator.translate(tarea.pagina.name, src='es', dest=idioma)
            return tarea.buscar_articulo_en_interwiki(idioma, traduccion.text)
        except:
            return None

    def get_name(self) -> str:
        return "Traducción"
