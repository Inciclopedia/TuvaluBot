from abc import ABC, abstractmethod
from typing import Generator

from mwclient import LoginError

from common.job import Job
from common.querybuilder import QueryBuilder

NAME = ""
DESCRIPTION = ""


class JobWithQuery(Job, ABC):

    @abstractmethod
    def __init__(self):
        super().__init__()

    @abstractmethod
    def process(self, article):
        pass

    @property
    @abstractmethod
    def querybuilder_title(self):
        raise NotImplementedError()

    def before_process(self):
        pass

    def after_process(self):
        pass

    def fetch_task_list(self) -> Generator[str, None, None]:
        if self.task_file == "":
            builder = QueryBuilder(self.client, self.querybuilder_title)
            query = builder.invoke()
            for page in query.invoke():
                yield page
        else:
            try:
                with open(self.task_file, "r", encoding='utf-8') as f:
                    for task in f.read().split('\n'):
                        yield task
            except Exception as e:
                print(self.lang.t("common.ioerror"))

    def task(self):
        self.before_process()
        for task in self.fetch_task_list():
            try:
                self.client.login(self.client.username, self.password)
            except LoginError:
                pass
            try:
                self.process(task)
            except Exception as e:
                self.logger.error(str(e))
        self.after_process()
        self.logger.info(self.lang.t("common.task_completed"))
