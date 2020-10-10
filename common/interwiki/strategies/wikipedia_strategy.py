from typing import Optional

from mwclient import Site
from mwclient.page import Page

from common.interwiki.interwikitask import InterwikiTask
from common.interwiki.strategies.interwikistrategy import InterwikiStrategy


class InterwikiWikipediaStrategy(InterwikiStrategy):

    def __init__(self, client: Site, wikipedia_api: str):
        super().__init__(client)
        self.wp_client = Site(wikipedia_api)

    def find_article_in_wikipedia(self, nombre) -> Optional[Page]:
        wp_article = Page(self.wp_client, nombre)
        if wp_article.redirect:
            wp_article = wp_article.resolve_redirect()
        return wp_article if wp_article.exists else None

    def get_name(self) -> str:
        return "Wikipedia"

    def run(self, task: InterwikiTask, language: str) -> Optional[str]:
        wp_article = self.find_article_in_wikipedia(task.page.name)
        if wp_article is not None:
            wp_interwikis = wp_article.langlinks()
            for wp_language, target in wp_interwikis:
                if language == wp_language:
                    return task.locate_article_on_interwiki(language, target)
        return None
