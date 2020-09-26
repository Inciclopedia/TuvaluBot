from typing import Union, Optional

from scripts.interwiki.estrategias.estrategia import Estrategia
from scripts.interwiki.tareainterwiki import TareaInterwiki


class EstrategiaNombreDirecto(Estrategia):
    def ejecutar(self, tarea: TareaInterwiki, idioma: str) -> Optional[str]:
        return tarea.buscar_articulo_en_interwiki(idioma, tarea.pagina.name)

    def get_name(self) -> str:
        return "Nombre Directo"
