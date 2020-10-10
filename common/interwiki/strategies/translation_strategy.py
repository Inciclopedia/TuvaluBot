from typing import Optional

from googletrans import Translator
from mwclient import Site

from common.interwiki.interwikitask import InterwikiTask
from common.interwiki.strategies.interwikistrategy import InterwikiStrategy


class InterwikiTranslationStrategy(InterwikiStrategy):

    def __init__(self, client: Site):
        super().__init__(client)
        self.translator = Translator()

    def run(self, task: InterwikiTask, language: str) -> Optional[str]:
        try:
            translation = self.translator.translate(task.page.name, src='es', dest=language)
            return task.locate_article_on_interwiki(language, translation.text)
        except:
            return None

    def get_name(self) -> str:
        return "Traducción"
