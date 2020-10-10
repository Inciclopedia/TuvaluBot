from abc import ABC, abstractmethod
from logging import Logger
from typing import List

from mwclient import Site
from mwclient.page import Page

from common.interwiki.interwikitask import InterwikiTask
from common.interwiki.strategies.interwikistrategy import InterwikiStrategy
from common.interwiki.strategies.namematch_strategy import InterwikiNameMatchStrategy
from common.interwiki.strategies.translation_strategy import InterwikiTranslationStrategy
from common.interwiki.strategies.wikipedia_strategy import InterwikiWikipediaStrategy
from common.job import Job
from domain.interwiki import Interwiki
from util.configimpl import Config
from util.lang import Lang

STRATEGIES = [InterwikiNameMatchStrategy, InterwikiWikipediaStrategy, InterwikiTranslationStrategy]


class InterwikiJob(Job, ABC):

    @abstractmethod
    def __init__(self):
        super().__init__()
        self.interwikis = None
        self.strategies = None

    def __init_strategies(self) -> List[InterwikiStrategy]:
        strategies = []
        for strategy in self.config.config["interwiki_strategies"]:
            module = __import__(strategy["package"], fromlist=[strategy["name"]])
            klass = getattr(module, strategy["name"])
            args = strategy["args"]
            args["client"] = self.client
            strategies.append(klass(**args))
        return strategies

    def bootstrap(self, client: Site, logger: Logger, task_file: str, password: str,
                  lang: Lang = None, config: Config = None):
        super().bootstrap(client, logger, task_file, password)
        self.interwikis = []
        for language, info in self.config.interwikis.items():
            self.interwikis.append(Interwiki(language, info["api"], info["fake"], info["skip"]))
        self.strategies = self.__init_strategies()

    def remap_interwikis(self, name):
        if not self.interwikis:
            raise ValueError("call bootstrap first!")
        page = Page(self.client, name)
        if page.redirect:
            return self.remap_interwikis(page.resolve_redirect().name)
        self.logger.info(self.lang.t("interwiki.remapping").format(name=name))
        task = InterwikiTask(page, self.client, self.interwikis, self.logger, self.lang)
        task.clean_broken_interwikis()
        missing = list(task.missing_interwikis())
        for language in missing:
            self.logger.debug(self.lang.t("interwiki.locating").format(lang=language))
            for strategy in self.strategies:
                self.logger.debug(self.lang.t("interwiki.attempting_strategy").format(strategy=strategy.get_name()))
                resultado = strategy.run(task, language)
                if resultado is not None:
                    break
        task.save_changes()
