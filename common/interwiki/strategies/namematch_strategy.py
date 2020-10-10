from typing import Optional

from common.interwiki.interwikitask import InterwikiTask
from common.interwiki.strategies.interwikistrategy import InterwikiStrategy


class InterwikiNameMatchStrategy(InterwikiStrategy):
    def run(self, task: InterwikiTask, language: str) -> Optional[str]:
        return task.locate_article_on_interwiki(language, task.page.name)

    def get_name(self) -> str:
        return "Nombre Directo"
