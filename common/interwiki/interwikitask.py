import re
from logging import Logger
from typing import List
from urllib.parse import quote

import requests
from mwclient import Site
from mwclient.page import Page

from domain.interwiki import Interwiki
from util.lang import Lang


class InterwikiTask(object):

    def __init__(self, page: Page, client: Site, interwikis: List[Interwiki], logger: Logger, lang: Lang):
        self.page = page
        self.wikitext = self.page.text()
        self.client = client
        self.interwiki_links = dict()
        for language, link in page.langlinks():
            if language not in self.interwiki_links:
                self.interwiki_links[language] = [link]
            else:
                self.interwiki_links[language].append(link)
        self.interwikis = interwikis
        self.logger = logger
        self.edited = False
        self.created = []
        self.deleted = []
        self.lang = lang

    def interwiki_exists(self, idioma):
        return idioma in self.interwiki_links

    def __fetch_interwiki(self, idioma):
        for iw in self.interwikis:
            if iw.language == idioma:
                return iw
        return None

    def get_interwiki_wikicode(self, idioma, articulo):
        interwiki = self.__fetch_interwiki(idioma)
        if interwiki is not None and interwiki.fake:
            interwiki_wikicode = "{{" + idioma + "|" + articulo + "}}"
        else:
            interwiki_wikicode = "[[" + idioma + ":" + articulo + "]]"
        return interwiki_wikicode

    def remove_interwiki(self, language, reason, article):
        self.logger.info(self.lang.t("interwiki.removing")
                         .format(reason=reason, lang=language, src=self.page.name, dest=article))
        self.edited = True
        self.wikitext = self.wikitext.replace(self.get_interwiki_wikicode(language, article), "")
        self.deleted.append(language)
        if language in self.interwiki_links:
            del self.interwiki_links[language]

    def create_interwiki(self, language, article):
        self.logger.info(self.lang.t("interwiki.creating").format(lang=language, src=self.page.name, dest=article))
        self.edited = True
        self.wikitext = self.wikitext + "\n" + self.get_interwiki_wikicode(language, article)
        self.created.append(language)

    def locate_article_on_interwiki(self, language, article, existed_earlier=False):
        interwiki = self.__fetch_interwiki(language)
        if interwiki is not None and interwiki.skip:
            return None
        if interwiki is None:
            self.logger.debug(self.lang.t("interwiki.dbg_obsolete")
                              .format(lang=language, src=self.page.name, dest=article))
            self.remove_interwiki(language, self.lang.t("interwiki.obsolete"), article)
            return None
        url = "http://" + interwiki.api + "/wiki/" + quote(article)
        try:
            response = requests.get(url)
        except:
            # some requests error , don't change stuff
            return article if existed_earlier else None
        if response.status_code == 404:
            self.logger.debug(self.lang.t("interwiki.dbg_not_found")
                              .format(lang=language, src=self.page.name, dest=article))
            if existed_earlier:
                self.remove_interwiki(language, self.lang.t("interwiki.not_found"), article)
            return None
        elif response.status_code == 200:
            self.logger.debug(self.lang.t("interwiki.dbg_found")
                              .format(lang=language, src=self.page.name, dest=article))
            if not existed_earlier:
                self.create_interwiki(language, article)
            return article
        else:
            # some other error , don't change stuff
            return article if existed_earlier else None

    def missing_interwikis(self):
        missing = []
        for interwiki in self.interwikis:
            found = False
            if not interwiki.fake:
                if interwiki.language in self.interwiki_links:
                    found = True
            else:
                if re.search(r"{{" + interwiki.language + r"\|[^}]+(?:}){2}\n", self.wikitext) is not None:
                    found = True
            if not found:
                missing.append(interwiki.language)
        return missing

    def clean_broken_interwikis(self):
        self.logger.debug(self.lang.t("interwiki.cleanup").format(name=self.page.name))
        for lang, articles in list(self.interwiki_links.items()):
            for article in articles:
                self.locate_article_on_interwiki(lang, article, existed_earlier=True)

    def generate_summary(self):
        tasks_done = []
        if len(self.created) > 0:
            tasks_done.append(self.lang.t("interwiki.reason_added") + ", ".join(self.created))
        if len(self.deleted) > 0:
            tasks_done.append(self.lang.t("interwiki.reason_removed") + ", ".join(self.deleted))
        return self.lang.t("interwiki.reason_header") + "; ".join(tasks_done)

    def save_changes(self):
        if self.edited:
            self.logger.info(self.lang.t("interwiki.saving").format(name=self.page.name))
            self.page.edit(self.wikitext, summary=self.generate_summary())
            self.created = []
            self.deleted = []
            self.edited = False
            self.page = Page(self.page.site, self.page.name)
            self.wikitext = self.page.text()
            self.interwiki_links = dict()
            for lang, link in self.page.langlinks():
                if lang not in self.interwiki_links:
                    self.interwiki_links[lang] = [link]
                else:
                    self.interwiki_links[lang].append(link)
